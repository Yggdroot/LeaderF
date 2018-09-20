/**
 * Copyright (C) 2018 Yggdroot
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>

#if defined(_MSC_VER)
#include <windows.h>
#else
#include <pthread.h>
#endif

#include "fuzzyEngine.h"
#include "fuzzyMatch.h"

typedef float weight_t;

typedef struct FeString
{
    char*    str;
    uint32_t len;
}FeString;

typedef struct FeTaskItem
{
    uint32_t offset;
    uint32_t length;
    uint32_t function;
}FeTaskItem;

typedef struct FeResult
{
    weight_t weight;
    uint32_t index;
}FeResult;

typedef struct FeCircularQueue
{
    void**          buffer;
    uint32_t        capacity;
    uint32_t        head;
    uint32_t        tail;
#if defined(_MSC_VER)
    uint32_t        done_num;
    uint32_t        task_count;
    CRITICAL_SECTION cs;
    HANDLE          task_sem;
    HANDLE          all_done_event;
#else
    uint32_t        unfinished_tasks;
    pthread_mutex_t mutex;
    pthread_cond_t  not_empty_cond;
    pthread_cond_t  task_cond;
#endif
}FeCircularQueue;

struct FuzzyEngine
{
    uint32_t        cpu_count;
#if defined(_MSC_VER)
    HANDLE*         threads;
#else
    pthread_t*      threads;
#endif
    PatternContext* pPattern_ctxt;
    uint8_t         is_name_only;
    FeString*       source;
    FeTaskItem*     tasks;
    union
    {
        weight_t*        weights;
        HighlightGroup** highlights;
    };
    FeCircularQueue task_queue;
};

#if defined(_MSC_VER)

#define QUEUE_INIT(queue, queue_capacity, ret_val)                                  \
    do {                                                                            \
        (queue).buffer = (void**)calloc((queue_capacity), sizeof(void*));           \
        if ( !(queue).buffer )                                                      \
        {                                                                           \
            fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);        \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
        (queue).capacity = (queue_capacity);                                        \
        (queue).head = (queue).tail = 0;                                            \
        (queue).done_num = 0;                                                       \
        (queue).task_count = 0;                                                     \
        InitializeCriticalSection(&(queue).cs);                                     \
        (queue).task_sem = CreateSemaphore(NULL, 0, 2048, NULL);                    \
        if ( !(queue).task_sem )                                                    \
        {                                                                           \
            fprintf(stderr, "CreateSemaphore error: %d\n", GetLastError());         \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
        /* auto-reset event */                                                      \
        (queue).all_done_event = CreateEvent(NULL, FALSE, FALSE, NULL);             \
        if ( !(queue).all_done_event )                                              \
        {                                                                           \
            fprintf(stderr, "CreateEvent error: %d\n", GetLastError());             \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
    } while(0)

#define QUEUE_SET_TASK_COUNT(queue, count)                                          \
    do {                                                                            \
        EnterCriticalSection(&(queue).cs);                                          \
        (queue).task_count = (count);                                               \
        LeaveCriticalSection(&(queue).cs);                                          \
    } while(0)

#define QUEUE_DESTROY(queue)                                                        \
    do {                                                                            \
        free((queue).buffer);                                                       \
        DeleteCriticalSection(&(queue).cs);                                         \
        CloseHandle((queue).task_sem);                                              \
        CloseHandle((queue).all_done_event);                                        \
    } while(0)

#define QUEUE_PUT(queue, pTask)                                                     \
    do {                                                                            \
        EnterCriticalSection(&(queue).cs);                                          \
        (queue).buffer[(queue).tail] = (void*)(pTask);                              \
        (queue).tail = ((queue).tail + 1) % (queue).capacity;                       \
        LeaveCriticalSection(&(queue).cs);                                          \
        if ( !ReleaseSemaphore((queue).task_sem, 1, NULL) )                         \
        {                                                                           \
            fprintf(stderr, "ReleaseSemaphore error: %d\n", GetLastError());        \
            break;                                                                  \
        }                                                                           \
    } while(0)

#define QUEUE_GET(queue, type, pTask)                                               \
    do {                                                                            \
        if ( WaitForSingleObject((queue).task_sem, INFINITE) == WAIT_FAILED )       \
        {                                                                           \
            fprintf(stderr, "WaitForSingleObject error: %d\n", GetLastError());     \
            break;                                                                  \
        }                                                                           \
        EnterCriticalSection(&(queue).cs);                                          \
        pTask = (type)(queue).buffer[(queue).head];                                 \
        (queue).head = ((queue).head + 1) % (queue).capacity;                       \
        LeaveCriticalSection(&(queue).cs);                                          \
    } while(0)

#define QUEUE_JOIN(queue)                                                           \
    do {                                                                            \
        if ( WaitForSingleObject((queue).all_done_event, INFINITE) == WAIT_FAILED ) \
        {                                                                           \
            fprintf(stderr, "WaitForSingleObject error: %d\n", GetLastError());     \
            break;                                                                  \
        }                                                                           \
        EnterCriticalSection(&(queue).cs);                                          \
        (queue).done_num = 0;                                                       \
        (queue).task_count = 0;                                                     \
        LeaveCriticalSection(&(queue).cs);                                          \
    } while(0)

#define QUEUE_TASK_DONE(queue)                                                      \
    do {                                                                            \
        EnterCriticalSection(&(queue).cs);                                          \
        ++(queue).done_num;                                                         \
        if ( (queue).done_num >= (queue).task_count )                               \
            SetEvent((queue).all_done_event);                                       \
        LeaveCriticalSection(&(queue).cs);                                          \
    } while(0)

#else

#define QUEUE_INIT(queue, queue_capacity, ret_val)                                  \
    do {                                                                            \
        (queue).buffer = (void**)calloc((queue_capacity), sizeof(void*));           \
        if ( !(queue).buffer )                                                      \
        {                                                                           \
            fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);        \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
        (queue).capacity = (queue_capacity);                                        \
        (queue).head = (queue).tail = 0;                                            \
        (queue).unfinished_tasks = 0;                                               \
        int ret;                                                                    \
        ret = pthread_mutex_init(&(queue).mutex, NULL);                             \
        if ( ret != 0 )                                                             \
        {                                                                           \
            fprintf(stderr, "pthread_mutex_init error!\n");                         \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
        ret = pthread_cond_init(&(queue).not_empty_cond, NULL);                     \
        if ( ret != 0 )                                                             \
        {                                                                           \
            fprintf(stderr, "pthread_cond_init error!\n");                          \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
        ret = pthread_cond_init(&(queue).task_cond, NULL);                          \
        if ( ret != 0 )                                                             \
        {                                                                           \
            fprintf(stderr, "pthread_cond_init error!\n");                          \
            ret_val = -1;                                                           \
            break;                                                                  \
        }                                                                           \
    } while(0)

#define QUEUE_DESTROY(queue)                                                        \
    do {                                                                            \
        free((queue).buffer);                                                       \
        pthread_mutex_destroy(&(queue).mutex);                                      \
        pthread_cond_destroy(&(queue).not_empty_cond);                              \
        pthread_cond_destroy(&(queue).task_cond);                                   \
    } while(0)

#define QUEUE_PUT(queue, pTask)                                                     \
    do {                                                                            \
        pthread_mutex_lock(&(queue).mutex);                                         \
        (queue).buffer[(queue).tail] = (void*)(pTask);                              \
        (queue).tail = ((queue).tail + 1) % (queue).capacity;                       \
        ++(queue).unfinished_tasks;                                                 \
        pthread_cond_signal(&(queue).not_empty_cond);                               \
        pthread_mutex_unlock(&(queue).mutex);                                       \
    } while(0)

#define QUEUE_GET(queue, type, pTask)                                               \
    do {                                                                            \
        pthread_mutex_lock(&(queue).mutex);                                         \
        while ( (queue).head == (queue).tail )                                      \
        {                                                                           \
            pthread_cond_wait(&(queue).not_empty_cond, &(queue).mutex);             \
        }                                                                           \
        pTask = (type)(queue).buffer[(queue).head];                                 \
        (queue).head = ((queue).head + 1) % (queue).capacity;                       \
        pthread_mutex_unlock(&(queue).mutex);                                       \
    } while(0)

#define QUEUE_JOIN(queue)                                                           \
    do {                                                                            \
        pthread_mutex_lock(&(queue).mutex);                                         \
        while ( (queue).unfinished_tasks > 0 )                                      \
        {                                                                           \
            pthread_cond_wait(&(queue).task_cond, &(queue).mutex);                  \
        }                                                                           \
        (queue).unfinished_tasks = 0;                                               \
        pthread_mutex_unlock(&(queue).mutex);                                       \
    } while(0)

#define QUEUE_TASK_DONE(queue)                                                      \
    do {                                                                            \
        pthread_mutex_lock(&(queue).mutex);                                         \
        --(queue).unfinished_tasks;                                                 \
        if ( (queue).unfinished_tasks <= 0 )                                        \
            pthread_cond_broadcast(&(queue).task_cond);                             \
        pthread_mutex_unlock(&(queue).mutex);                                       \
    } while(0)

#endif

#define MIN(a, b) ((a) < (b) ? (a) : (b))

#define MAX_TASK_COUNT(cpu_count) ((cpu_count) << 3)

enum
{
    GETWEIGHT = 0,
    GETHIGHLIGHTS
};

#if defined(_MSC_VER)
static DWORD WINAPI _worker(LPVOID pParam)
#else
static void* _worker(void* pParam)
#endif
{
    FuzzyEngine* pEngine = (FuzzyEngine*)pParam;

    while ( 1 )
    {
        FeTaskItem* pTask = NULL;
        QUEUE_GET(pEngine->task_queue, FeTaskItem*, pTask);

        if ( pTask )
        {
            FeString* tasks = pEngine->source + pTask->offset;
            if ( pTask->function == GETWEIGHT )
            {
                weight_t* results = pEngine->weights + pTask->offset;
                uint32_t length = pTask->length;
                uint32_t i = 0;
                for ( ; i < length; ++i )
                {
                    results[i] = getWeight(tasks[i].str, tasks[i].len,
                                           pEngine->pPattern_ctxt, pEngine->is_name_only);
                }
            }
            else
            {
                HighlightGroup** results = pEngine->highlights + pTask->offset;
                uint32_t length = pTask->length;
                uint32_t i = 0;
                for ( ; i < length; ++i )
                {
                    results[i] = getHighlights(tasks[i].str, tasks[i].len,
                                               pEngine->pPattern_ctxt, pEngine->is_name_only);
                }
            }

            QUEUE_TASK_DONE(pEngine->task_queue);
        }
        else
        {
            break;
        }
    }

#if defined(_MSC_VER)
    return 0;
#else
    return NULL;
#endif
}

FuzzyEngine* createFuzzyEngine(uint32_t cpu_count)
{
    FuzzyEngine* pEngine = (FuzzyEngine*)malloc(sizeof(FuzzyEngine));
    if ( !pEngine )
    {
        return NULL;
    }

    pEngine->cpu_count = cpu_count;
    pEngine->threads = NULL;
    pEngine->pPattern_ctxt = NULL;
    pEngine->source = NULL;
    pEngine->tasks = NULL;

    int32_t ret = 0;
    QUEUE_INIT(pEngine->task_queue, MAX_TASK_COUNT(cpu_count) + cpu_count + 1, ret);
    if ( ret != 0 )
    {
        free(pEngine);
        return NULL;
    }

    return pEngine;
}

void closeFuzzyEngine(FuzzyEngine* pEngine)
{
    if ( !pEngine )
        return;

    /**
     * pEngine->threads is NULL if fuzzyMatch() is not called,
     * or fuzzyMatch() returns before malloc for pEngine->threads.
     */
    if ( pEngine->threads )
    {
        uint32_t i = 0;
        for ( ; i < pEngine->cpu_count; ++i )
        {
            QUEUE_PUT(pEngine->task_queue, NULL);
        }

#if defined(_MSC_VER)
        WaitForMultipleObjects(pEngine->cpu_count, pEngine->threads, TRUE, INFINITE);
        for ( i = 0; i < pEngine->cpu_count; ++i )
        {
            CloseHandle(pEngine->threads[i]);
        }
#else
        for ( i = 0; i < pEngine->cpu_count; ++i )
        {
            pthread_join(pEngine->threads[i], NULL);
        }
#endif
        free(pEngine->threads);
    }

    QUEUE_DESTROY(pEngine->task_queue);
    free(pEngine);
}

static int32_t pyObject_ToStringAndSize(PyObject* obj, char** buffer, uint32_t* size)
{
#if PY_MAJOR_VERSION >= 3
    *buffer = (char*)PyUnicode_AsUTF8AndSize(obj, (Py_ssize_t*)size);
    if ( buffer )
        return 0;
    else
        return -1;
#else
    if ( PyString_AsStringAndSize(obj, buffer, (Py_ssize_t*)size) >= 0 )
        return 0;
    else
        return -1;
#endif
}

/* sort in descending order */
static int compare(const void* a, const void* b)
{
    weight_t wa = ((const FeResult*)a)->weight;
    weight_t wb = ((const FeResult*)b)->weight;
    return (wa < wb) - (wa > wb);
}

static void delFuzzyEngine(PyObject* obj)
{
    closeFuzzyEngine((FuzzyEngine*)PyCapsule_GetPointer(obj, NULL));
}

/**
 * createFuzzyEngine(cpu_count, auto_free=False)
 *
 * `auto_free` is optional that specifies whether auto free the fuzzyEngine object.
 *      It defaults to `False`, which means do not auto free the fuzzyEngine object,
 *      so that you should call closeFuzzyEngine() manually.
 *  return a fuzzyEngine object
 */
static PyObject* fuzzyEngine_createFuzzyEngine(PyObject* self, PyObject* args, PyObject* kwargs)
{
    uint32_t cpu_count;
    uint8_t  auto_free = 0;
    static char* kwlist[] = {"cpu_count", "auto_free", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "I|b:createFuzzyEngine", kwlist, &cpu_count, &auto_free) )
        return NULL;

    FuzzyEngine* pEngine = createFuzzyEngine(cpu_count);

    return PyCapsule_New(pEngine, NULL, auto_free ? delFuzzyEngine : NULL);
}

/**
 * closeFuzzyEngine(engine)
 */
static PyObject* fuzzyEngine_closeFuzzyEngine(PyObject* self, PyObject* args)
{
    PyObject* engine = NULL;
    if ( !PyArg_ParseTuple(args, "O:closeFuzzyEngine", &engine) )
        return NULL;

    closeFuzzyEngine((FuzzyEngine*)PyCapsule_GetPointer(engine, NULL));

    Py_RETURN_NONE;
}

static void delPatternContext(PyObject* obj)
{
    free(PyCapsule_GetPointer(obj, NULL));
}

/**
 * initPattern(pattern)
 */
static PyObject* fuzzyEngine_initPattern(PyObject* self, PyObject* args)
{
    char* pattern;
    Py_ssize_t pattern_len;

    if ( !PyArg_ParseTuple(args, "s#:initPattern", &pattern, &pattern_len) )
        return NULL;

    PatternContext* pCtxt = initPattern(pattern, pattern_len);

    return PyCapsule_New(pCtxt, NULL, delPatternContext);
}

/**
 * fuzzyMatch(engine, source, pattern, is_name_only=False, sort_results=True)
 *
 * `is_name_only` is optional, it defaults to `False`, which indicates using the full path matching algorithm.
 * `sort_results` is optional, it defineds to `True`, which indicates whether to sort the results.
 *
 * return a tuple, (a list of corresponding weight, a sorted list of items from `source` that match `pattern`).
 */
static PyObject* fuzzyEngine_fuzzyMatch(PyObject* self, PyObject* args, PyObject* kwargs)
{
    PyObject* py_engine = NULL;
    PyObject* py_source = NULL;
    PyObject* py_patternCtxt = NULL;
    uint8_t is_name_only = 0;
    uint8_t sort_results = 1;
    static char* kwlist[] = {"engine", "source", "pattern", "is_name_only", "sort_results", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "OOO|bb:fuzzyMatch", kwlist, &py_engine,
                                      &py_source, &py_patternCtxt, &is_name_only, &sort_results) )
        return NULL;

    FuzzyEngine* pEngine = (FuzzyEngine*)PyCapsule_GetPointer(py_engine, NULL);
    if ( !pEngine )
        return NULL;

    if ( !PyList_Check(py_source) )
    {
        PyErr_SetString(PyExc_TypeError, "parameter `source` must be a list.");
        return NULL;
    }

    uint32_t source_size = (uint32_t)PyList_Size(py_source);
    if ( source_size == 0 )
    {
        return Py_BuildValue("([],[])");
    }

    pEngine->pPattern_ctxt = (PatternContext*)PyCapsule_GetPointer(py_patternCtxt, NULL);
    if ( !pEngine->pPattern_ctxt )
        return NULL;

    pEngine->is_name_only = is_name_only;

    uint32_t max_task_count  = MAX_TASK_COUNT(pEngine->cpu_count);
    uint32_t chunk_size = (source_size + max_task_count - 1) / max_task_count;
    uint32_t task_count = (source_size + chunk_size - 1) / chunk_size;

    pEngine->source = (FeString*)malloc(source_size * sizeof(FeString));
    if ( !pEngine->source )
    {
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->tasks = (FeTaskItem*)malloc(task_count * sizeof(FeTaskItem));
    if ( !pEngine->tasks )
    {
        free(pEngine->source);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->weights = (weight_t*)malloc(source_size * sizeof(weight_t));
    if ( !pEngine->weights )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    FeResult* results = (FeResult*)malloc(source_size * sizeof(FeResult));
    if ( !results )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        free(pEngine->weights);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    if ( !pEngine->threads )
    {
#if defined(_MSC_VER)
        pEngine->threads = (HANDLE*)malloc(pEngine->cpu_count * sizeof(HANDLE));
#else
        pEngine->threads = (pthread_t*)malloc(pEngine->cpu_count * sizeof(pthread_t));
#endif
        if ( !pEngine->threads )
        {
            free(pEngine->source);
            free(pEngine->tasks);
            free(pEngine->weights);
            free(results);
            fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
            return NULL;
        }

        uint32_t i = 0;
        for ( ; i < pEngine->cpu_count; ++i)
        {
#if defined(_MSC_VER)
            pEngine->threads[i] = CreateThread(NULL, 0, _worker, pEngine, 0, NULL);
            if ( !pEngine->threads[i] )
#else
            int ret = pthread_create(&pEngine->threads[i], NULL, _worker, pEngine);
            if ( ret != 0 )
#endif
            {
                free(pEngine->source);
                free(pEngine->tasks);
                free(pEngine->weights);
                free(results);
                free(pEngine->threads);
                fprintf(stderr, "pthread_create error!\n");
                return NULL;
            }
        }
    }

#if defined(_MSC_VER)
    QUEUE_SET_TASK_COUNT(pEngine->task_queue, task_count);
#endif

    uint32_t i = 0;
    for ( ; i < task_count; ++i )
    {
        uint32_t offset = i * chunk_size;
        uint32_t length = MIN(chunk_size, source_size - offset);

        pEngine->tasks[i].offset = offset;
        pEngine->tasks[i].length = length;
        pEngine->tasks[i].function = GETWEIGHT;

        uint32_t j = 0;
        for ( ; j < length; ++j )
        {
            FeString *s = pEngine->source + offset + j;
            PyObject* item = PyList_GET_ITEM(py_source, offset + j);
            if ( pyObject_ToStringAndSize(item, &s->str, &s->len) < 0 )
            {
                free(pEngine->source);
                free(pEngine->tasks);
                free(pEngine->weights);
                free(results);
                fprintf(stderr, "pyObject_ToStringAndSize error!\n");
                return NULL;
            }
        }

        QUEUE_PUT(pEngine->task_queue, pEngine->tasks + i);
    }

    QUEUE_JOIN(pEngine->task_queue);    /* blocks until all tasks have finished */

    uint32_t results_count = 0;
    for ( i = 0; i < source_size; ++i )
    {
        if ( pEngine->weights[i] > MIN_WEIGHT )
        {
            results[results_count].weight = pEngine->weights[i];
            results[results_count].index = i;
            ++results_count;
        }
    }

    if ( results_count == 0 )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        free(pEngine->weights);
        free(results);
        return Py_BuildValue("([],[])");
    }

    if ( sort_results )
    {
        qsort(results, results_count, sizeof(FeResult), compare);
    }

    PyObject* weight_list = PyList_New(results_count);
    PyObject* text_list = PyList_New(results_count);
    for ( i = 0; i < results_count; ++i )
    {
        /* PyList_SET_ITEM() steals a reference to item.     */
        /* PySequence_GetItem() return value: New reference. */
        PyList_SET_ITEM(weight_list, i, Py_BuildValue("f", results[i].weight));
        PyList_SET_ITEM(text_list, i, PySequence_GetItem(py_source, results[i].index));
    }

    free(pEngine->source);
    free(pEngine->tasks);
    free(pEngine->weights);
    free(results);

    return Py_BuildValue("(NN)", weight_list, text_list);
}

/**
 * fuzzyMatchEx(engine, source, pattern, is_name_only=False, sort_results=True)
 *
 * same as fuzzyMatch(), the only difference is the return value.
 * return a tuple, (a list of corresponding weight, a sorted list of index to items from `source` that match `pattern`).
 */
static PyObject* fuzzyEngine_fuzzyMatchEx(PyObject* self, PyObject* args, PyObject* kwargs)
{
    PyObject* py_engine = NULL;
    PyObject* py_source = NULL;
    PyObject* py_patternCtxt = NULL;
    uint8_t is_name_only = 0;
    uint8_t sort_results = 1;
    static char* kwlist[] = {"engine", "source", "pattern", "is_name_only", "sort_results", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "OOO|bb:fuzzyMatch", kwlist, &py_engine,
                                      &py_source, &py_patternCtxt, &is_name_only, &sort_results) )
        return NULL;

    FuzzyEngine* pEngine = (FuzzyEngine*)PyCapsule_GetPointer(py_engine, NULL);
    if ( !pEngine )
        return NULL;

    if ( !PyList_Check(py_source) )
    {
        PyErr_SetString(PyExc_TypeError, "parameter `source` must be a list.");
        return NULL;
    }

    uint32_t source_size = (uint32_t)PyList_Size(py_source);
    if ( source_size == 0 )
    {
        return Py_BuildValue("([],[])");
    }

    pEngine->pPattern_ctxt = (PatternContext*)PyCapsule_GetPointer(py_patternCtxt, NULL);
    if ( !pEngine->pPattern_ctxt )
        return NULL;

    pEngine->is_name_only = is_name_only;

    uint32_t max_task_count  = MAX_TASK_COUNT(pEngine->cpu_count);
    uint32_t chunk_size = (source_size + max_task_count - 1) / max_task_count;
    uint32_t task_count = (source_size + chunk_size - 1) / chunk_size;

    pEngine->source = (FeString*)malloc(source_size * sizeof(FeString));
    if ( !pEngine->source )
    {
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->tasks = (FeTaskItem*)malloc(task_count * sizeof(FeTaskItem));
    if ( !pEngine->tasks )
    {
        free(pEngine->source);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->weights = (weight_t*)malloc(source_size * sizeof(weight_t));
    if ( !pEngine->weights )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    FeResult* results = (FeResult*)malloc(source_size * sizeof(FeResult));
    if ( !results )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        free(pEngine->weights);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    if ( !pEngine->threads )
    {
#if defined(_MSC_VER)
        pEngine->threads = (HANDLE*)malloc(pEngine->cpu_count * sizeof(HANDLE));
#else
        pEngine->threads = (pthread_t*)malloc(pEngine->cpu_count * sizeof(pthread_t));
#endif
        if ( !pEngine->threads )
        {
            free(pEngine->source);
            free(pEngine->tasks);
            free(pEngine->weights);
            free(results);
            fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
            return NULL;
        }

        uint32_t i = 0;
        for ( ; i < pEngine->cpu_count; ++i)
        {
#if defined(_MSC_VER)
            pEngine->threads[i] = CreateThread(NULL, 0, _worker, pEngine, 0, NULL);
            if ( !pEngine->threads[i] )
#else
            int ret = pthread_create(&pEngine->threads[i], NULL, _worker, pEngine);
            if ( ret != 0 )
#endif
            {
                free(pEngine->source);
                free(pEngine->tasks);
                free(pEngine->weights);
                free(results);
                free(pEngine->threads);
                fprintf(stderr, "pthread_create error!\n");
                return NULL;
            }
        }
    }

#if defined(_MSC_VER)
    QUEUE_SET_TASK_COUNT(pEngine->task_queue, task_count);
#endif

    uint32_t i = 0;
    for ( ; i < task_count; ++i )
    {
        uint32_t offset = i * chunk_size;
        uint32_t length = MIN(chunk_size, source_size - offset);

        pEngine->tasks[i].offset = offset;
        pEngine->tasks[i].length = length;
        pEngine->tasks[i].function = GETWEIGHT;

        uint32_t j = 0;
        for ( ; j < length; ++j )
        {
            FeString *s = pEngine->source + offset + j;
            PyObject* item = PyList_GET_ITEM(py_source, offset + j);
            if ( pyObject_ToStringAndSize(item, &s->str, &s->len) < 0 )
            {
                free(pEngine->source);
                free(pEngine->tasks);
                free(pEngine->weights);
                free(results);
                fprintf(stderr, "pyObject_ToStringAndSize error!\n");
                return NULL;
            }
        }

        QUEUE_PUT(pEngine->task_queue, pEngine->tasks + i);
    }

    QUEUE_JOIN(pEngine->task_queue);    /* blocks until all tasks have finished */

    uint32_t results_count = 0;
    for ( i = 0; i < source_size; ++i )
    {
        if ( pEngine->weights[i] > MIN_WEIGHT )
        {
            results[results_count].weight = pEngine->weights[i];
            results[results_count].index = i;
            ++results_count;
        }
    }

    if ( results_count == 0 )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        free(pEngine->weights);
        free(results);
        return Py_BuildValue("([],[])");
    }

    if ( sort_results )
    {
        qsort(results, results_count, sizeof(FeResult), compare);
    }

    PyObject* weight_list = PyList_New(results_count);
    PyObject* index_list = PyList_New(results_count);
    for ( i = 0; i < results_count; ++i )
    {
        /* PyList_SET_ITEM() steals a reference to item.     */
        /* PySequence_GetItem() return value: New reference. */
        PyList_SET_ITEM(weight_list, i, Py_BuildValue("f", results[i].weight));
        PyList_SET_ITEM(index_list, i, Py_BuildValue("I", results[i].index));
    }

    free(pEngine->source);
    free(pEngine->tasks);
    free(pEngine->weights);
    free(results);

    return Py_BuildValue("(NN)", weight_list, index_list);
}

/**
 * getHighlights(engine, source, pattern, is_name_only=False)
 *
 * `is_name_only` is optional, it defaults to `False`, which indicates using the full path matching algorithm.
 *
 * return a list of list of pair [col, length], where `col` is the column number(start from 1, the value must
 * correspond to the byte index of `text`) and `length` is the length of the highlight in bytes.
 * e.g., [
 *          [ [2,3], [6,2], [10,4], ... ],
 *          [ [3,2], [5,2], [9,3], ... ],
 *          ...
 *       ]
 *  NOTE: this function must be called after fuzzyMatch() is called, because this function assume that all the
 *  texts in `source` match `pattern` and all the threads in FuzzyEngine have already been started.
 */
static PyObject* fuzzyEngine_getHighlights(PyObject* self, PyObject* args, PyObject* kwargs)
{
    PyObject* py_source = NULL;
    PyObject* py_patternCtxt = NULL;
    PyObject* py_engine = NULL;
    uint8_t is_name_only = 0;
    static char* kwlist[] = {"engine", "source", "pattern", "is_name_only", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "OOO|b:fuzzyMatch", kwlist, &py_engine,
                                      &py_source, &py_patternCtxt, &is_name_only) )
        return NULL;

    FuzzyEngine* pEngine = (FuzzyEngine*)PyCapsule_GetPointer(py_engine, NULL);
    if ( !pEngine )
        return NULL;

    if ( !PyList_Check(py_source) )
    {
        PyErr_SetString(PyExc_TypeError, "parameter `source` must be a list.");
        return NULL;
    }

    pEngine->pPattern_ctxt = (PatternContext*)PyCapsule_GetPointer(py_patternCtxt, NULL);
    if ( !pEngine->pPattern_ctxt )
        return NULL;

    pEngine->is_name_only = is_name_only;

    uint32_t source_size = (uint32_t)PyList_Size(py_source);

    uint32_t max_task_count  = MAX_TASK_COUNT(pEngine->cpu_count);
    uint32_t chunk_size = (source_size + max_task_count - 1) / max_task_count;
    uint32_t task_count = (source_size + chunk_size - 1) / chunk_size;

    pEngine->source = (FeString*)malloc(source_size * sizeof(FeString));
    if ( !pEngine->source )
    {
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->tasks = (FeTaskItem*)malloc(task_count * sizeof(FeTaskItem));
    if ( !pEngine->tasks )
    {
        free(pEngine->source);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

    pEngine->highlights = (HighlightGroup**)malloc(source_size * sizeof(HighlightGroup*));
    if ( !pEngine->highlights )
    {
        free(pEngine->source);
        free(pEngine->tasks);
        fprintf(stderr, "Out of memory at %s:%d\n", __FILE__, __LINE__);
        return NULL;
    }

#if defined(_MSC_VER)
    QUEUE_SET_TASK_COUNT(pEngine->task_queue, task_count);
#endif

    uint32_t i = 0;
    for ( ; i < task_count; ++i )
    {
        uint32_t offset = i * chunk_size;
        uint32_t length = MIN(chunk_size, source_size - offset);

        pEngine->tasks[i].offset = offset;
        pEngine->tasks[i].length = length;
        pEngine->tasks[i].function = GETHIGHLIGHTS;

        uint32_t j = 0;
        for ( ; j < length; ++j )
        {
            FeString *s = pEngine->source + offset + j;
            PyObject* item = PyList_GET_ITEM(py_source, offset + j);
            if ( pyObject_ToStringAndSize(item, &s->str, &s->len) < 0 )
            {
                free(pEngine->source);
                free(pEngine->tasks);
                free(pEngine->highlights);
                fprintf(stderr, "pyObject_ToStringAndSize error!\n");
                return NULL;
            }
        }

        QUEUE_PUT(pEngine->task_queue, pEngine->tasks + i);
    }

    QUEUE_JOIN(pEngine->task_queue);    /* blocks until all tasks have finished */

    PyObject* res = PyList_New(source_size);
    for ( i = 0; i < source_size; ++i )
    {
        HighlightGroup* pGroup = pEngine->highlights[i];
        if ( !pGroup )
        {
            free(pEngine->source);
            free(pEngine->tasks);
            free(pEngine->highlights);
            Py_XDECREF(res);
            return NULL;
        }

        PyObject* list = PyList_New(pGroup->end_index);
        uint16_t j;
        for ( j = 0; j < pGroup->end_index; ++j )
        {
            PyList_SetItem(list, j, Py_BuildValue("[H,H]", pGroup->positions[j].col, pGroup->positions[j].len));
        }
        PyList_SetItem(res, i, list);
        free(pGroup);
    }

    return res;
}

static PyMethodDef fuzzyEngine_Methods[] =
{
    { "createFuzzyEngine", (PyCFunction)fuzzyEngine_createFuzzyEngine, METH_VARARGS | METH_KEYWORDS, "" },
    { "closeFuzzyEngine", (PyCFunction)fuzzyEngine_closeFuzzyEngine, METH_VARARGS, "" },
    { "initPattern", (PyCFunction)fuzzyEngine_initPattern, METH_VARARGS, "initialize the pattern." },
    { "fuzzyMatch", (PyCFunction)fuzzyEngine_fuzzyMatch, METH_VARARGS | METH_KEYWORDS, "" },
    { "fuzzyMatchEx", (PyCFunction)fuzzyEngine_fuzzyMatchEx, METH_VARARGS | METH_KEYWORDS, "" },
    { "getHighlights", (PyCFunction)fuzzyEngine_getHighlights, METH_VARARGS | METH_KEYWORDS, "" },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef fuzzyEngine_module =
{
    PyModuleDef_HEAD_INIT,
    "fuzzyEngine",   /* name of module */
    "fuzzy matching algorithm which takes full advantage of the cpu cores.",
    -1,
    fuzzyEngine_Methods
};

PyMODINIT_FUNC PyInit_fuzzyEngine(void)
{
    return PyModule_Create(&fuzzyEngine_module);
}

#else

PyMODINIT_FUNC initfuzzyEngine(void)
{
    Py_InitModule("fuzzyEngine", fuzzyEngine_Methods);
}

#endif

