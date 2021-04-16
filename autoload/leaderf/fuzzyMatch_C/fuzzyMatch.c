/**
 * Copyright (C) 2017 Yggdroot
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

#ifndef PY_SSIZE_T_CLEAN
    #define PY_SSIZE_T_CLEAN
#endif

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "fuzzyMatch.h"


#if defined(_MSC_VER) && \
    (defined(_M_IX86) || defined(_M_AMD64) || defined(_M_X64))

    #define FM_BITSCAN_WINDOWS

    #include <intrin.h>
    #pragma intrinsic(_BitScanReverse)

    #if defined(_M_AMD64) || defined(_M_X64)
        #define FM_BITSCAN_WINDOWS64
        #pragma intrinsic(_BitScanReverse64)
    #endif

#endif

#if defined(FM_BITSCAN_WINDOWS)

    uint32_t FM_BitLength(uint64_t x)
    {
        unsigned long index;
        #if defined(FM_BITSCAN_WINDOWS64)
        if ( !_BitScanReverse64(&index, x) )
            return 0;
        else
            return index + 1;
        #else
        if ( (x & 0xFFFFFFFF00000000) == 0 )
        {
            if ( !_BitScanReverse(&index, (unsigned long)x) )
                return 0;
            else
                return index + 1;
        }
        else
        {
            _BitScanReverse(&index, (unsigned long)(x >> 32));
            return index + 33;
        }
        #endif
    }

    #define FM_BIT_LENGTH(x) FM_BitLength(x)

#elif defined(__GNUC__)

    #define FM_BIT_LENGTH(x) ((uint32_t)(8 * sizeof(unsigned long long) - __builtin_clzll(x)))

#elif defined(__clang__)

    #if __has_builtin(__builtin_clzll)
        #define FM_BIT_LENGTH(x) ((uint32_t)(8 * sizeof(unsigned long long) - __builtin_clzll(x)))
    #endif

#endif

#if !defined(FM_BIT_LENGTH)

    static uint8_t clz_table_8bit[256] =
    {
        8, 7, 6, 6, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4,
        3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    };

    uint32_t FM_BIT_LENGTH(uint64_t x)
    {
        uint32_t n = 0;
        if ((x & 0xFFFFFFFF00000000) == 0) {n  = 32; x <<= 32;}
        if ((x & 0xFFFF000000000000) == 0) {n += 16; x <<= 16;}
        if ((x & 0xFF00000000000000) == 0) {n +=  8; x <<=  8;}
        n += (uint32_t)clz_table_8bit[x >> 56];

        return 64 - n;
    }

#endif

static uint64_t deBruijn = 0x022FDD63CC95386D;

static uint8_t MultiplyDeBruijnBitPosition[64] =
{
    0,  1,  2,  53, 3,  7,  54, 27,
    4,  38, 41, 8,  34, 55, 48, 28,
    62, 5,  39, 46, 44, 42, 22, 9,
    24, 35, 59, 56, 49, 18, 29, 11,
    63, 52, 6,  26, 37, 40, 33, 47,
    61, 45, 43, 21, 23, 58, 17, 10,
    51, 25, 36, 32, 60, 20, 57, 16,
    50, 31, 19, 15, 30, 14, 13, 12,
};

#define FM_CTZ(x) MultiplyDeBruijnBitPosition[((uint64_t)((x) & -(int64_t)(x)) * deBruijn) >> 58]

static uint16_t valTable[64] =
{
    0,   1,   4,   7,   13,  19,  25,  31,
    37,  43,  49,  55,  61,  67,  73,  79,
    85,  91,  97,  103, 109, 115, 121, 127,
    133, 139, 145, 151, 157, 163, 169, 175,
    181, 187, 193, 199, 205, 211, 217, 223,
    229, 235, 241, 247, 253, 259, 265, 271,
    277, 283, 289, 295, 301, 307, 313, 319,
    325, 331, 337, 343, 349, 355, 361, 367
};

typedef struct TextContext
{
    const char* text;
    uint64_t* text_mask;
    uint16_t text_len;
    uint16_t col_num;
    uint16_t offset;
}TextContext;

typedef struct ValueElements
{
    float score;
    uint16_t beg;
    uint16_t end;
}ValueElements;

PatternContext* initPattern(const char* pattern, uint16_t pattern_len)
{
    PatternContext* pPattern_ctxt = (PatternContext*)malloc(sizeof(PatternContext));
    if ( !pPattern_ctxt )
    {
        fprintf(stderr, "Out of memory in initPattern()!\n");
        return NULL;
    }
    pPattern_ctxt->actual_pattern_len = pattern_len;
    if ( pattern_len >= 64 )
    {
        pattern_len = 63;
    }
    pPattern_ctxt->pattern = pattern;
    pPattern_ctxt->pattern_len = pattern_len;
    memset(pPattern_ctxt->pattern_mask, -1, sizeof(pPattern_ctxt->pattern_mask));

    uint16_t i;
    for ( i = 0; i < pattern_len; ++i )
    {
        pPattern_ctxt->pattern_mask[(uint8_t)pattern[i]] ^= (1LL << i);
        if ( islower(pattern[i]) && pPattern_ctxt->pattern_mask[(uint8_t)toupper(pattern[i])] != -1 )
        {
            pPattern_ctxt->pattern_mask[(uint8_t)toupper(pattern[i])] ^= (1LL << i);
        }
    }
    pPattern_ctxt->is_lower = 1;

    for ( i = 0; i < pattern_len; ++i )
    {
        if ( isupper(pattern[i]) )
        {
            pPattern_ctxt->is_lower = 0;
            break;
        }
    }

    return pPattern_ctxt;
}

ValueElements* evaluate_nameOnly(TextContext* pText_ctxt,
                                 PatternContext* pPattern_ctxt,
                                 uint16_t k,
                                 ValueElements val[])
{
    uint64_t* text_mask = pText_ctxt->text_mask;
    uint16_t col_num = pText_ctxt->col_num;
    uint16_t j = pText_ctxt->offset;

    const char* pattern = pPattern_ctxt->pattern;
    uint16_t base_offset = pattern[k] * col_num;
    uint64_t x = text_mask[base_offset + (j >> 6)] >> (j & 63);
    uint16_t i = 0;

    if ( x == 0 )
    {
        uint64_t bits = 0;
        uint16_t col = 0;
        for ( col = (j >> 6) + 1; col < col_num; ++col )
        {
            if ( (bits = text_mask[base_offset + col]) != 0 )
                break;
        }
        if ( bits == 0 )
        {
            memset(val, 0, sizeof(ValueElements));
            return val;
        }
        else
        {
            i = (col << 6) + FM_CTZ(bits);
        }
    }
    else
    {
        i = j + FM_CTZ(x);
    }

    /**
     * e.g., text = '~abc~~AbcD~~', pattern = 'abcd'
     * j > 0 means val[k].beg > 0, means k in val
     */
    if ( j > 0 && val[k].beg >= j )
        return val + k;

    uint16_t beg = 0;
    uint16_t end = 0;

    uint16_t max_prefix_score = 0;
    float max_score = MIN_WEIGHT;

    const char* text = pText_ctxt->text;
    uint16_t text_len = pText_ctxt->text_len;
    uint16_t pattern_len = pPattern_ctxt->pattern_len - k;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;

    uint16_t special = 0;
    if ( i == 0 )
        special = 3;
    else if ( isupper(text[i]) )
        special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
    /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
    /*     special = 3;                                                     */
    /* else if ( text[i-1] == '.' )                                         */
    /*     special = 3;                                                     */
    else if ( !isalnum(text[i-1]) )
        special = 3;
    else
        special = 0;
    ++i;
    int64_t d = -2;     /* ~1 */
    int64_t last = d;
    while ( i < text_len )
    {
        last = d;
        char c = text[i];
        /* c in pattern */
        if ( pattern_mask[(uint8_t)c] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)c] >> k);
        /**
         * text = 'xxABC', pattern = 'abc'; text[i] == 'B'
         * text = 'xxABC', pattern = 'abc'; text[i] == 'C'
         * NOT text = 'xxABCd', pattern = 'abc'; text[i] == 'C'
         * 'Cd' is considered as a word
         */
        else if ( isupper(text[i-1]) && pattern_mask[(uint8_t)tolower(c)] != -1
                  && (i+1 == text_len || !islower(text[i+1])) )
            d = (d << 1) | (pattern_mask[(uint8_t)tolower(c)] >> k);
        else
            d = ~0;

        if ( d >= last )
        {
            float score = MIN_WEIGHT;
            uint16_t end_pos = 0;
            uint16_t n = FM_BIT_LENGTH(~last);
            /* e.g., text = '~~abcd~~~~', pattern = 'abcd' */
            if ( n == pattern_len )
            {
                score = (float)(special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n]);
                if ( special > 0 )
                {
                    val[k].score = score;
                    val[k].beg = i - n;
                    val[k].end = i;
                    return val + k;
                }
                else
                    end_pos = i;
            }
            else
            {
                uint16_t prefix_score = special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n];
                if ( prefix_score > max_prefix_score )
                {
                    max_prefix_score = prefix_score;
                    pText_ctxt->offset = i;
                    ValueElements* pVal = evaluate_nameOnly(pText_ctxt, pPattern_ctxt, k + n, val);
                    if ( pVal->end )
                    {
                        score = prefix_score + pVal->score - 0.2f * (pVal->beg - i);
                        end_pos = pVal->end;
                    }
                }
            }
            if ( score > max_score )
            {
                max_score = score;
                beg = i - n;
                end = end_pos;
            }
            /* e.g., text = '~_ababc~~~~', pattern = 'abc' */
            special = 0;
        }

        /*
         * e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
         * to find the index of the second 'a'
         * `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
         */
        if ( d == ~0 || d == last )
        {
            x = text_mask[base_offset + (i >> 6)] >> (i & 63);

            if ( x == 0 )
            {
                uint64_t bits = 0;
                uint16_t col = 0;
                for ( col = (i >> 6) + 1; col < col_num; ++col )
                {
                    if ( (bits = text_mask[base_offset + col]) != 0 )
                        break;
                }
                if ( bits == 0 )
                    break;
                else
                    i = (col << 6) + FM_CTZ(bits);
            }
            else
            {
                i += FM_CTZ(x);
            }

            if ( isupper(text[i]) )
                special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
            /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
            /*     special = 3;                                                     */
            /* else if ( text[i-1] == '.' )                                         */
            /*     special = 3;                                                     */
            else if ( !isalnum(text[i-1]) )
                special = 3;
            else
                special = 0;
            d = -2;
            ++i;
        }
        else
            ++i;
    }

    /* e.g., text = '~~~~abcd', pattern = 'abcd' */
    if ( i == text_len )
    {
        if ( ~d >> (pattern_len - 1) )
        {
            float score = (float)(special > 0 ? (pattern_len > 1 ? valTable[pattern_len + 1] : valTable[pattern_len]) + special
                            : valTable[pattern_len]);
            if ( score > max_score )
            {
                max_score = score;
                beg = i - pattern_len;
                end = i;
            }
        }
    }

    val[k].score = max_score;
    val[k].beg = beg;
    val[k].end = end;

    return val + k;
}

ValueElements* evaluate(TextContext* pText_ctxt,
                        PatternContext* pPattern_ctxt,
                        uint16_t k,
                        ValueElements val[])
{
    uint64_t* text_mask = pText_ctxt->text_mask;
    uint16_t col_num = pText_ctxt->col_num;
    uint16_t j = pText_ctxt->offset;

    const char* pattern = pPattern_ctxt->pattern;
    uint16_t base_offset = pattern[k] * col_num;
    uint64_t x = text_mask[base_offset + (j >> 6)] >> (j & 63);
    uint16_t i = 0;

    if ( x == 0 )
    {
        uint64_t bits = 0;
        uint16_t col = 0;
        for ( col = (j >> 6) + 1; col < col_num; ++col )
        {
            if ( (bits = text_mask[base_offset + col]) != 0 )
                break;
        }
        if ( bits == 0 )
        {
            memset(val, 0, sizeof(ValueElements));
            return val;
        }
        else
        {
            i = (col << 6) + FM_CTZ(bits);
        }
    }
    else
    {
        i = j + FM_CTZ(x);
    }

    /**
     * e.g., text = '~abc~~AbcD~~', pattern = 'abcd'
     * j > 0 means val[k].beg > 0, means k in val
     */
    if ( j > 0 && val[k].beg >= j )
        return val + k;

    uint16_t beg = 0;
    uint16_t end = 0;

    uint16_t max_prefix_score = 0;
    float max_score = MIN_WEIGHT;

    const char* text = pText_ctxt->text;
    uint16_t text_len = pText_ctxt->text_len;
    uint16_t pattern_len = pPattern_ctxt->pattern_len - k;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;

    uint16_t special = 0;
    if ( i == 0 )
        special = 5;
#if defined(_MSC_VER)
    else if ( text[i-1] == '\\' || text[i-1] == '/' )
#else
    else if ( text[i-1] == '/' )
#endif
        special = k == 0 ? 5 : 3;
    else if ( isupper(text[i]) )
        special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
    /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
    /*     special = 3;                                                     */
    /* else if ( text[i-1] == '.' )                                         */
    /*     special = 3;                                                     */
    else if ( !isalnum(text[i-1]) )
        special = 3;
    else
        special = 0;
    ++i;
    int64_t d = -2;     /* ~1 */
    int64_t last = d;
    while ( i < text_len )
    {
        last = d;
        char c = text[i];
        /* c in pattern */
        if ( pattern_mask[(uint8_t)c] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)c] >> k);
        /**
         * text = 'xxABC', pattern = 'abc'; text[i] == 'B'
         * text = 'xxABC', pattern = 'abc'; text[i] == 'C'
         * NOT text = 'xxABCd', pattern = 'abc'; text[i] == 'C'
         * 'Cd' is considered as a word
         */
        /* else if ( isupper(text[i-1]) && pattern_mask[(uint8_t)tolower(c)] != -1 */
        /*           && (i+1 == text_len || !islower(text[i+1])) )                 */
        else if ( pattern_mask[(uint8_t)tolower(c)] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)tolower(c)] >> k);
        else
            d = ~0;

        if ( d >= last )
        {
            float score = MIN_WEIGHT;
            uint16_t end_pos = 0;
            uint16_t n = FM_BIT_LENGTH(~last);
            /* e.g., text = '~~abcd~~~~', pattern = 'abcd' */
            if ( n == pattern_len )
            {
                score = (float)(special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n]);
                if ( (k == 0 && special == 5) || (k > 0 && special > 0) )
                {
                    val[k].score = score;
                    val[k].beg = i - n;
                    val[k].end = i;
                    return val + k;
                }
                else
                    end_pos = i;
            }
            else
            {
                uint16_t prefix_score = special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n];
                /**
                 * e.g., text = 'AbcxxAbcyyde', pattern = 'abcde'
                 * prefer matching 'Abcyyde'
                 */
                if ( prefix_score > max_prefix_score
                     || (special > 0 && prefix_score == max_prefix_score) )
                {
                    max_prefix_score = prefix_score;
                    pText_ctxt->offset = i;
                    ValueElements* pVal = evaluate(pText_ctxt, pPattern_ctxt, k + n, val);
                    if ( pVal->end )
                    {
                        score = prefix_score + pVal->score - 0.3f * (pVal->beg - i);
                        end_pos = pVal->end;
                    }
                }
            }
            if ( score > max_score )
            {
                max_score = score;
                beg = i - n;
                end = end_pos;
            }
            /* e.g., text = '~_ababc~~~~', pattern = 'abc' */
            special = 0;
        }

        /*
         * e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
         * to find the index of the second 'a'
         * `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
         */
        if ( d == ~0 || d == last )
        {
            x = text_mask[base_offset + (i >> 6)] >> (i & 63);

            if ( x == 0 )
            {
                uint64_t bits = 0;
                uint16_t col = 0;
                for ( col = (i >> 6) + 1; col < col_num; ++col )
                {
                    if ( (bits = text_mask[base_offset + col]) != 0 )
                        break;
                }
                if ( bits == 0 )
                    break;
                else
                    i = (col << 6) + FM_CTZ(bits);
            }
            else
            {
                i += FM_CTZ(x);
            }

#if defined(_MSC_VER)
            if ( text[i-1] == '\\' || text[i-1] == '/' )
#else
            if ( text[i-1] == '/' )
#endif
                special = k == 0 ? 5 : 3;
            else if ( isupper(text[i]) )
                special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
            /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
            /*     special = 3;                                                     */
            /* else if ( text[i-1] == '.' )                                         */
            /*     special = 3;                                                     */
            else if ( !isalnum(text[i-1]) )
                special = 3;
            else
                special = 0;
            d = -2;
            ++i;
        }
        else
            ++i;
    }

    /* e.g., text = '~~~~abcd', pattern = 'abcd' */
    if ( i == text_len )
    {
        if ( ~d >> (pattern_len - 1) )
        {
            float score = (float)(special > 0 ? (pattern_len > 1 ? valTable[pattern_len + 1] : valTable[pattern_len]) + special
                            : valTable[pattern_len]);
            if ( score > max_score )
            {
                max_score = score;
                beg = i - pattern_len;
                end = i;
            }
        }
    }

    val[k].score = max_score;
    val[k].beg = beg;
    val[k].end = end;

    return val + k;
}

float getWeight(const char* text, uint16_t text_len,
                PatternContext* pPattern_ctxt,
                uint8_t is_name_only)
{
    if ( !text || !pPattern_ctxt )
        return MIN_WEIGHT;

    uint16_t j = 0;
    uint16_t col_num = 0;
    uint64_t* text_mask = NULL;
    const char* pattern = pPattern_ctxt->pattern;
    uint16_t pattern_len = pPattern_ctxt->pattern_len;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;
    char first_char = pattern[0];
    char last_char = pattern[pattern_len - 1];

    /* maximum number of int16_t is (1 << 15) - 1 */
    if ( text_len >= (1 << 15) )
    {
        text_len = (1 << 15) - 1;
    }

    if ( pattern_len == 1 )
    {
        if ( isupper(first_char) )
        {
            int16_t first_char_pos = -1;
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( text[i] == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
            if ( first_char_pos == -1 )
                return MIN_WEIGHT;
            else
                return 1.0f/(first_char_pos + 1) + 1.0f/text_len;
        }
        else
        {
            int16_t first_char_pos = -1;
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( tolower(text[i]) == first_char )
                {
                    if ( first_char_pos == -1 )
                        first_char_pos = i;

                    if ( isupper(text[i]) || i == 0 || !isalnum(text[i-1]) )
                        return 2 + 1.0f/(i + 1) + 1.0f/text_len;
                }
            }
            if ( first_char_pos == -1 )
                return MIN_WEIGHT;
            else
                return 1.0f/(first_char_pos + 1) + 1.0f/text_len;
        }
    }

    int16_t first_char_pos = -1;
    if ( pPattern_ctxt->is_lower )
    {
        int16_t i;
        for ( i = 0; i < text_len; ++i )
        {
            if ( tolower(text[i]) == first_char )
            {
                first_char_pos = i;
                break;
            }
        }
        if ( first_char_pos == -1 )
            return MIN_WEIGHT;

        int16_t last_char_pos = -1;
        for ( i = text_len - 1; i >= first_char_pos; --i )
        {
            if ( tolower(text[i]) == last_char )
            {
                last_char_pos = i;
                break;
            }
        }
        if ( last_char_pos == -1 )
            return MIN_WEIGHT;

        col_num = (text_len + 63) >> 6;     /* (text_len + 63)/64 */
        /* uint64_t text_mask[256][col_num] */
        text_mask = (uint64_t*)calloc(col_num << 8, sizeof(uint64_t));
        if ( !text_mask )
        {
            fprintf(stderr, "Out of memory in getWeight()!\n");
            return MIN_WEIGHT;
        }
        char c;
        for ( i = first_char_pos; i <= last_char_pos; ++i )
        {
            c = tolower(text[i]);
            /* c in pattern */
            if ( pattern_mask[(uint8_t)c] != -1 )
            {
                text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
                if ( j < pattern_len && c == pattern[j] )
                    ++j;
            }
        }
    }
    else
    {
        if ( isupper(first_char) )
        {
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( text[i] == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
        }
        else
        {
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( tolower(text[i]) == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
        }
        if ( first_char_pos == -1 )
            return MIN_WEIGHT;

        int16_t last_char_pos = -1;
        if ( isupper(last_char) )
        {
            int16_t i;
            for ( i = text_len - 1; i >= first_char_pos; --i )
            {
                if ( text[i] == last_char )
                {
                    last_char_pos = i;
                    break;
                }
            }
        }
        else
        {
            int16_t i;
            for ( i = text_len - 1; i >= first_char_pos; --i )
            {
                if ( tolower(text[i]) == last_char )
                {
                    last_char_pos = i;
                    break;
                }
            }
        }
        if ( last_char_pos == -1 )
            return MIN_WEIGHT;

        col_num = (text_len + 63) >> 6;
        /* uint64_t text_mask[256][col_num] */
        text_mask = (uint64_t*)calloc(col_num << 8, sizeof(uint64_t));
        if ( !text_mask )
        {
            fprintf(stderr, "Out of memory in getWeight()!\n");
            return MIN_WEIGHT;
        }
        char c;
        int16_t i;
        for ( i = first_char_pos; i <= last_char_pos; ++i )
        {
            c = text[i];
            if ( isupper(c) )
            {
                /* c in pattern */
                if ( pattern_mask[(uint8_t)c] != -1 )
                    text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
                if ( pattern_mask[(uint8_t)tolower(c)] != -1 )
                    text_mask[(uint8_t)tolower(c) * col_num + (i >> 6)] |= 1ULL << (i & 63);
                if ( j < pattern_len && c == toupper(pattern[j]) )
                    ++j;
            }
            else
            {
                /* c in pattern */
                if ( pattern_mask[(uint8_t)c] != -1 )
                {
                    text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
                    if ( j < pattern_len && c == pattern[j] )
                        ++j;
                }
            }
        }
    }

    if ( j < pattern_len )
    {
        free(text_mask);
        return MIN_WEIGHT;
    }

    if ( pPattern_ctxt->actual_pattern_len >= 64 )
    {
        int16_t i;
        j = 0;
        for ( i = first_char_pos; i < text_len; ++i )
        {
            if ( j < pPattern_ctxt->actual_pattern_len )
            {
                if ( text[i] == pattern[j] )
                {
                    ++j;
                }
            }
            else
                break;
        }

        if ( j < pPattern_ctxt->actual_pattern_len )
        {
            free(text_mask);
            return MIN_WEIGHT;
        }
    }

    TextContext text_ctxt;
    text_ctxt.text = text;
    text_ctxt.text_len = text_len;
    text_ctxt.text_mask = text_mask;
    text_ctxt.col_num = col_num;
    text_ctxt.offset = 0;

    ValueElements val[64];
    memset(val, 0, sizeof(val));
    if ( is_name_only )
    {
        ValueElements* pVal = evaluate_nameOnly(&text_ctxt, pPattern_ctxt, 0, val);
        float score = pVal->score;
        uint16_t beg = pVal->beg;
        uint16_t end = pVal->end;

        free(text_mask);

        return score + (1 >> beg) + 1.0f/(beg + end) + 1.0f/text_len;
    }
    else
    {
        ValueElements* pVal = evaluate(&text_ctxt, pPattern_ctxt, 0, val);
        float score = pVal->score;
        uint16_t beg = pVal->beg;

        free(text_mask);

        return score + (float)pattern_len/text_len + (float)(pattern_len << 1)/(text_len - beg);
    }
}


HighlightGroup* evaluateHighlights_nameOnly(TextContext* pText_ctxt,
                                            PatternContext* pPattern_ctxt,
                                            uint16_t k,
                                            HighlightGroup* groups[])
{
    uint16_t j = pText_ctxt->offset;

    if ( groups[k] && groups[k]->beg >= j )
        return groups[k];

    uint64_t* text_mask = pText_ctxt->text_mask;
    uint16_t col_num = pText_ctxt->col_num;

    const char* pattern = pPattern_ctxt->pattern;
    uint16_t base_offset = pattern[k] * col_num;
    uint64_t x = text_mask[base_offset + (j >> 6)] >> (j & 63);
    uint16_t i = 0;

    if ( x == 0 )
    {
        uint64_t bits = 0;
        uint16_t col = 0;
        for ( col = (j >> 6) + 1; col < col_num; ++col )
        {
            if ( (bits = text_mask[base_offset + col]) != 0 )
                break;
        }
        if ( bits == 0 )
        {
            return NULL;
        }
        else
        {
            i = (col << 6) + FM_CTZ(bits);
        }
    }
    else
    {
        i = j + FM_CTZ(x);
    }

    uint16_t max_prefix_score = 0;
    float max_score = MIN_WEIGHT;

    if ( !groups[k] )
    {
        groups[k] = (HighlightGroup*)calloc(1, sizeof(HighlightGroup));
        if ( !groups[k] )
        {
            fprintf(stderr, "Out of memory in evaluateHighlights_nameOnly()!\n");
            return NULL;
        }
    }
    else
    {
        memset(groups[k], 0, sizeof(HighlightGroup));
    }

    HighlightGroup cur_highlights;
    memset(&cur_highlights, 0, sizeof(HighlightGroup));

    const char* text = pText_ctxt->text;
    uint16_t text_len = pText_ctxt->text_len;
    uint16_t pattern_len = pPattern_ctxt->pattern_len - k;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;

    uint16_t special = 0;
    if ( i == 0 )
        special = 3;
    else if ( isupper(text[i]) )
        special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
    /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
    /*     special = 3;                                                     */
    /* else if ( text[i-1] == '.' )                                         */
    /*     special = 3;                                                     */
    else if ( !isalnum(text[i-1]) )
        special = 3;
    else
        special = 0;
    ++i;
    int64_t d = -2;     /* ~1 */
    int64_t last = d;
    while ( i < text_len )
    {
        last = d;
        char c = text[i];
        /* c in pattern */
        if ( pattern_mask[(uint8_t)c] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)c] >> k);
        /**
         * text = 'xxABC', pattern = 'abc'; text[i] == 'B'
         * text = 'xxABC', pattern = 'abc'; text[i] == 'C'
         * NOT text = 'xxABCd', pattern = 'abc'; text[i] == 'C'
         * 'Cd' is considered as a word
         */
        else if ( isupper(text[i-1]) && pattern_mask[(uint8_t)tolower(c)] != -1
                  && (i+1 == text_len || !islower(text[i+1])) )
            d = (d << 1) | (pattern_mask[(uint8_t)tolower(c)] >> k);
        else
            d = ~0;

        if ( d >= last )
        {
            float score = MIN_WEIGHT;
            uint16_t n = FM_BIT_LENGTH(~last);
            /* e.g., text = '~~abcd~~~~', pattern = 'abcd' */
            if ( n == pattern_len )
            {
                score = (float)(special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n]);
                cur_highlights.score = score;
                cur_highlights.beg = i - n;
                cur_highlights.end = i;
                cur_highlights.end_index = 1;
                cur_highlights.positions[0].col = i - n + 1;
                cur_highlights.positions[0].len = n;
                if ( special > 0 )
                {
                    memcpy(groups[k], &cur_highlights, sizeof(HighlightGroup));
                    return groups[k];
                }
            }
            else
            {
                uint16_t prefix_score = special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n];
                if ( prefix_score > max_prefix_score )
                {
                    max_prefix_score = prefix_score;
                    pText_ctxt->offset = i;
                    HighlightGroup* pGroup = evaluateHighlights_nameOnly(pText_ctxt, pPattern_ctxt, k + n, groups);
                    if ( pGroup )
                    {
                        if ( pGroup->end )
                        {
                            score = prefix_score + pGroup->score - 0.2f * (pGroup->beg - i);
                            cur_highlights.score = score;
                            cur_highlights.beg = i - n;
                            cur_highlights.end = pGroup->end;
                            cur_highlights.positions[0].col = i - n + 1;
                            cur_highlights.positions[0].len = n;
                            memcpy(cur_highlights.positions + 1, pGroup->positions, pGroup->end_index * sizeof(HighlightPos));
                            cur_highlights.end_index = pGroup->end_index + 1;
                        }
                    }
                }
            }
            if ( score > max_score )
            {
                max_score = score;
                memcpy(groups[k], &cur_highlights, sizeof(HighlightGroup));
            }
            /* e.g., text = '~_ababc~~~~', pattern = 'abc' */
            special = 0;
        }

        /*
         * e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
         * to find the index of the second 'a'
         * `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
         */
        if ( d == ~0 || d == last )
        {
            x = text_mask[base_offset + (i >> 6)] >> (i & 63);

            if ( x == 0 )
            {
                uint64_t bits = 0;
                uint16_t col = 0;
                for ( col = (i >> 6) + 1; col < col_num; ++col )
                {
                    if ( (bits = text_mask[base_offset + col]) != 0 )
                        break;
                }
                if ( bits == 0 )
                    break;
                else
                    i = (col << 6) + FM_CTZ(bits);
            }
            else
            {
                i += FM_CTZ(x);
            }

            if ( isupper(text[i]) )
                special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
            /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
            /*     special = 3;                                                     */
            /* else if ( text[i-1] == '.' )                                         */
            /*     special = 3;                                                     */
            else if ( !isalnum(text[i-1]) )
                special = 3;
            else
                special = 0;
            d = -2;
            ++i;
        }
        else
            ++i;
    }

    /* e.g., text = '~~~~abcd', pattern = 'abcd' */
    if ( i == text_len )
    {
        if ( ~d >> (pattern_len - 1) )
        {
            float score = (float)(special > 0 ? (pattern_len > 1 ? valTable[pattern_len + 1] : valTable[pattern_len]) + special
                            : valTable[pattern_len]);
            if ( score > max_score )
            {
                groups[k]->score = score;
                groups[k]->beg = i - pattern_len;
                groups[k]->end = i;
                groups[k]->positions[0].col = i - pattern_len + 1;
                groups[k]->positions[0].len = pattern_len;
                groups[k]->end_index = 1;
            }
        }
    }

    return groups[k];
}


HighlightGroup* evaluateHighlights(TextContext* pText_ctxt,
                                   PatternContext* pPattern_ctxt,
                                   uint16_t k,
                                   HighlightGroup* groups[])
{
    uint16_t j = pText_ctxt->offset;

    if ( groups[k] && groups[k]->beg >= j )
        return groups[k];

    uint64_t* text_mask = pText_ctxt->text_mask;
    uint16_t col_num = pText_ctxt->col_num;

    const char* pattern = pPattern_ctxt->pattern;
    uint16_t base_offset = pattern[k] * col_num;
    uint64_t x = text_mask[base_offset + (j >> 6)] >> (j & 63);
    uint16_t i = 0;

    if ( x == 0 )
    {
        uint64_t bits = 0;
        uint16_t col = 0;
        for ( col = (j >> 6) + 1; col < col_num; ++col )
        {
            if ( (bits = text_mask[base_offset + col]) != 0 )
                break;
        }
        if ( bits == 0 )
        {
            return NULL;
        }
        else
        {
            i = (col << 6) + FM_CTZ(bits);
        }
    }
    else
    {
        i = j + FM_CTZ(x);
    }

    uint16_t max_prefix_score = 0;
    float max_score = MIN_WEIGHT;

    if ( !groups[k] )
    {
        groups[k] = (HighlightGroup*)calloc(1, sizeof(HighlightGroup));
        if ( !groups[k] )
        {
            fprintf(stderr, "Out of memory in evaluateHighlights()!\n");
            return NULL;
        }
    }
    else
    {
        memset(groups[k], 0, sizeof(HighlightGroup));
    }

    HighlightGroup cur_highlights;
    memset(&cur_highlights, 0, sizeof(HighlightGroup));

    const char* text = pText_ctxt->text;
    uint16_t text_len = pText_ctxt->text_len;
    uint16_t pattern_len = pPattern_ctxt->pattern_len - k;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;

    uint16_t special = 0;
    if ( i == 0 )
        special = 5;
#if defined(_MSC_VER)
    else if ( text[i-1] == '\\' || text[i-1] == '/' )
#else
    else if ( text[i-1] == '/' )
#endif
        special = k == 0 ? 5 : 3;
    else if ( isupper(text[i]) )
        special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
    /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
    /*     special = 3;                                                     */
    /* else if ( text[i-1] == '.' )                                         */
    /*     special = 3;                                                     */
    else if ( !isalnum(text[i-1]) )
        special = 3;
    else
        special = 0;
    ++i;
    int64_t d = -2;     /* ~1 */
    int64_t last = d;
    while ( i < text_len )
    {
        last = d;
        char c = text[i];
        /* c in pattern */
        if ( pattern_mask[(uint8_t)c] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)c] >> k);
        /**
         * text = 'xxABC', pattern = 'abc'; text[i] == 'B'
         * text = 'xxABC', pattern = 'abc'; text[i] == 'C'
         * NOT text = 'xxABCd', pattern = 'abc'; text[i] == 'C'
         * 'Cd' is considered as a word
         */
        /* else if ( isupper(text[i-1]) && pattern_mask[(uint8_t)tolower(c)] != -1 */
        /*           && (i+1 == text_len || !islower(text[i+1])) )                 */
        else if ( pattern_mask[(uint8_t)tolower(c)] != -1 )
            d = (d << 1) | (pattern_mask[(uint8_t)tolower(c)] >> k);
        else
            d = ~0;

        if ( d >= last )
        {
            float score = MIN_WEIGHT;
            uint16_t n = FM_BIT_LENGTH(~last);
            /* e.g., text = '~~abcd~~~~', pattern = 'abcd' */
            if ( n == pattern_len )
            {
                score = (float)(special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n]);
                cur_highlights.score = score;
                cur_highlights.beg = i - n;
                cur_highlights.end = i;
                cur_highlights.end_index = 1;
                cur_highlights.positions[0].col = i - n + 1;
                cur_highlights.positions[0].len = n;
                if ( (k == 0 && special == 5) || (k > 0 && special > 0) )
                {
                    memcpy(groups[k], &cur_highlights, sizeof(HighlightGroup));
                    return groups[k];
                }
            }
            else
            {
                uint16_t prefix_score = special > 0 ? (n > 1 ? valTable[n+1] : valTable[n]) + special : valTable[n];
                /**
                 * e.g., text = 'AbcxxAbcyyde', pattern = 'abcde'
                 * prefer matching 'Abcyyde'
                 */
                if ( prefix_score > max_prefix_score
                     || (special > 0 && prefix_score == max_prefix_score) )
                {
                    max_prefix_score = prefix_score;
                    pText_ctxt->offset = i;
                    HighlightGroup* pGroup = evaluateHighlights(pText_ctxt, pPattern_ctxt, k + n, groups);
                    if ( pGroup )
                    {
                        if ( pGroup->end )
                        {
                            score = prefix_score + pGroup->score - 0.3f * (pGroup->beg - i);
                            cur_highlights.score = score;
                            cur_highlights.beg = i - n;
                            cur_highlights.end = pGroup->end;
                            cur_highlights.positions[0].col = i - n + 1;
                            cur_highlights.positions[0].len = n;
                            memcpy(cur_highlights.positions + 1, pGroup->positions, pGroup->end_index * sizeof(HighlightPos));
                            cur_highlights.end_index = pGroup->end_index + 1;
                        }
                    }
                }
            }
            if ( score > max_score )
            {
                max_score = score;
                memcpy(groups[k], &cur_highlights, sizeof(HighlightGroup));
            }
            /* e.g., text = '~_ababc~~~~', pattern = 'abc' */
            special = 0;
        }

        /*
         * e.g., text = 'a~c~~~~ab~c', pattern = 'abc',
         * to find the index of the second 'a'
         * `d == last` is for the case when text = 'kpi_oos1', pattern = 'kos'
         */
        if ( d == ~0 || d == last )
        {
            x = text_mask[base_offset + (i >> 6)] >> (i & 63);

            if ( x == 0 )
            {
                uint64_t bits = 0;
                uint16_t col = 0;
                for ( col = (i >> 6) + 1; col < col_num; ++col )
                {
                    if ( (bits = text_mask[base_offset + col]) != 0 )
                        break;
                }
                if ( bits == 0 )
                    break;
                else
                    i = (col << 6) + FM_CTZ(bits);
            }
            else
            {
                i += FM_CTZ(x);
            }

#if defined(_MSC_VER)
            if ( text[i-1] == '\\' || text[i-1] == '/' )
#else
            if ( text[i-1] == '/' )
#endif
                special = k == 0 ? 5 : 3;
            else if ( isupper(text[i]) )
                special = !isupper(text[i-1]) || (i+1 < text_len && islower(text[i+1])) ? 3 : 0;
            /* else if ( text[i-1] == '_' || text[i-1] == '-' || text[i-1] == ' ' ) */
            /*     special = 3;                                                     */
            /* else if ( text[i-1] == '.' )                                         */
            /*     special = 3;                                                     */
            else if ( !isalnum(text[i-1]) )
                special = 3;
            else
                special = 0;
            d = -2;
            ++i;
        }
        else
            ++i;
    }

    /* e.g., text = '~~~~abcd', pattern = 'abcd' */
    if ( i == text_len )
    {
        if ( ~d >> (pattern_len - 1) )
        {
            float score = (float)(special > 0 ? (pattern_len > 1 ? valTable[pattern_len + 1] : valTable[pattern_len]) + special
                            : valTable[pattern_len]);
            if ( score > max_score )
            {
                groups[k]->score = score;
                groups[k]->beg = i - pattern_len;
                groups[k]->end = i;
                groups[k]->positions[0].col = i - pattern_len + 1;
                groups[k]->positions[0].len = pattern_len;
                groups[k]->end_index = 1;
            }
        }
    }

    return groups[k];
}

/**
 * return a list of pair [col, length], where `col` is the column number(start
 * from 1, the value must correspond to the byte index of `text`) and `length`
 * is the length of the highlight in bytes.
 * e.g., [ [2,3], [6,2], [10,4], ... ]
 */
HighlightGroup* getHighlights(const char* text,
                              uint16_t text_len,
                              PatternContext* pPattern_ctxt,
                              uint8_t is_name_only)
{
    if ( !text || !pPattern_ctxt )
        return NULL;

    uint16_t col_num = 0;
    uint64_t* text_mask = NULL;
    const char* pattern = pPattern_ctxt->pattern;
    uint16_t pattern_len = pPattern_ctxt->pattern_len;
    int64_t* pattern_mask = pPattern_ctxt->pattern_mask;
    char first_char = pattern[0];
    char last_char = pattern[pattern_len - 1];

    /* maximum number of int16_t is (1 << 15) - 1 */
    if ( text_len >= (1 << 15) )
    {
        text_len = (1 << 15) - 1;
    }

    if ( pattern_len == 1 )
    {
        if ( isupper(first_char) )
        {
            int16_t first_char_pos = -1;
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( text[i] == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
            if ( first_char_pos == -1 )
                return NULL;
            else
            {
                HighlightGroup* pGroup = (HighlightGroup*)malloc(sizeof(HighlightGroup));
                if ( !pGroup )
                {
                    fprintf(stderr, "Out of memory in getHighlights()!\n");
                    return NULL;
                }
                pGroup->positions[0].col = first_char_pos + 1;
                pGroup->positions[0].len = 1;
                pGroup->end_index = 1;

                return pGroup;
            }
        }
        else
        {
            int16_t first_char_pos = -1;
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( tolower(text[i]) == first_char )
                {
                    if ( first_char_pos == -1 )
                        first_char_pos = i;

                    if ( isupper(text[i]) || i == 0 || !isalnum(text[i-1]) )
                    {
                        first_char_pos = i;
                        break;
                    }
                }
            }
            if ( first_char_pos == -1 )
                return NULL;
            else
            {
                HighlightGroup* pGroup = (HighlightGroup*)malloc(sizeof(HighlightGroup));
                if ( !pGroup )
                {
                    fprintf(stderr, "Out of memory in getHighlights()!\n");
                    return NULL;
                }
                pGroup->positions[0].col = first_char_pos + 1;
                pGroup->positions[0].len = 1;
                pGroup->end_index = 1;

                return pGroup;
            }
        }
    }

    if ( pPattern_ctxt->is_lower )
    {
        int16_t first_char_pos = -1;
        int16_t i;
        for ( i = 0; i < text_len; ++i )
        {
            if ( tolower(text[i]) == first_char )
            {
                first_char_pos = i;
                break;
            }
        }

        int16_t last_char_pos = -1;
        for ( i = text_len - 1; i >= first_char_pos; --i )
        {
            if ( tolower(text[i]) == last_char )
            {
                last_char_pos = i;
                break;
            }
        }

        col_num = (text_len + 63) >> 6;     /* (text_len + 63)/64 */
        /* uint64_t text_mask[256][col_num] */
        text_mask = (uint64_t*)calloc(col_num << 8, sizeof(uint64_t));
        if ( !text_mask )
        {
            fprintf(stderr, "Out of memory in getHighlights()!\n");
            return NULL;
        }
        char c;
        for ( i = first_char_pos; i <= last_char_pos; ++i )
        {
            c = tolower(text[i]);
            /* c in pattern */
            if ( pattern_mask[(uint8_t)c] != -1 )
                text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
        }
    }
    else
    {
        int16_t first_char_pos = -1;
        if ( isupper(first_char) )
        {
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( text[i] == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
        }
        else
        {
            int16_t i;
            for ( i = 0; i < text_len; ++i )
            {
                if ( tolower(text[i]) == first_char )
                {
                    first_char_pos = i;
                    break;
                }
            }
        }

        int16_t last_char_pos = -1;
        if ( isupper(last_char) )
        {
            int16_t i;
            for ( i = text_len - 1; i >= first_char_pos; --i )
            {
                if ( text[i] == last_char )
                {
                    last_char_pos = i;
                    break;
                }
            }
        }
        else
        {
            int16_t i;
            for ( i = text_len - 1; i >= first_char_pos; --i )
            {
                if ( tolower(text[i]) == last_char )
                {
                    last_char_pos = i;
                    break;
                }
            }
        }

        col_num = (text_len + 63) >> 6;
        /* uint64_t text_mask[256][col_num] */
        text_mask = (uint64_t*)calloc(col_num << 8, sizeof(uint64_t));
        if ( !text_mask )
        {
            fprintf(stderr, "Out of memory in getHighlights()!\n");
            return NULL;
        }

        char c;
        int16_t i;
        for ( i = first_char_pos; i <= last_char_pos; ++i )
        {
            c = text[i];
            if ( isupper(c) )
            {
                /* c in pattern */
                if ( pattern_mask[(uint8_t)c] != -1 )
                    text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
                if ( pattern_mask[(uint8_t)tolower(c)] != -1 )
                    text_mask[(uint8_t)tolower(c) * col_num + (i >> 6)] |= 1ULL << (i & 63);
            }
            else
            {
                /* c in pattern */
                if ( pattern_mask[(uint8_t)c] != -1 )
                    text_mask[(uint8_t)c * col_num + (i >> 6)] |= 1ULL << (i & 63);
            }
        }
    }

    TextContext text_ctxt;
    text_ctxt.text = text;
    text_ctxt.text_len = text_len;
    text_ctxt.text_mask = text_mask;
    text_ctxt.col_num = col_num;
    text_ctxt.offset = 0;

    /* HighlightGroup* groups[pattern_len] */
    HighlightGroup** groups = (HighlightGroup**)calloc(pattern_len, sizeof(HighlightGroup*));
    if ( !groups )
    {
        fprintf(stderr, "Out of memory in getHighlights()!\n");
        free(text_mask);
        return NULL;
    }

    HighlightGroup* pGroup = NULL;
    if ( is_name_only )
        pGroup = evaluateHighlights_nameOnly(&text_ctxt, pPattern_ctxt, 0, groups);
    else
        pGroup = evaluateHighlights(&text_ctxt, pPattern_ctxt, 0, groups);

    free(text_mask);
    uint16_t i;
    for ( i = 0; i < pattern_len; ++i )
    {
        if ( groups[i] && groups[i] != pGroup )
            free(groups[i]);
    }
    free(groups);

    return pGroup;
}

/**
 * e.g., /usr/src/example.tar.gz
 * `dirname` is "/usr/src"
 * `basename` is "example.tar.gz"
 * `filename` is "example.tar", `suffix` is ".gz"
 */
uint32_t getPathWeight(const char* filename,
                       const char* suffix,
                       const char* dirname,
                       const char* path, uint32_t path_len)
{
    uint32_t filename_lcp = 0;
    uint32_t filename_prefix = 0;
    uint32_t dirname_lcp = 0;
    uint32_t is_suffix_diff = 0;
    uint32_t is_basename_same = 0;
    uint32_t is_dirname_same = 0;

    const char* filename_start = path;
    const char* p = path + path_len;
    const char* p1 = NULL;

    while ( p >= path )
    {
#if defined(_MSC_VER)
        if ( *p == '\\' || *p == '/' )
#else
        if ( *p == '/' )
#endif
        {
            filename_start = p + 1;
            break;
        }
        --p;
    }
    
    if ( *suffix != '\0' )
    {
        p = filename_start;
        p1 = filename;
        while ( *p != '\0' && *p == *p1 )
        {
            ++filename_lcp;
            ++p;
            ++p1;
        }

        filename_prefix = filename_lcp;

        if ( filename_lcp > 0 )
        {
            if ( (*p >= 'a' && *p <= 'z') || (*p >= '0' && *p <= '9')
                 || (*p1 >= 'a' && *p1 <= 'z') || (*p1 >= '0' && *p1 <= '9') )
            {
                --p;
                while ( p > filename_start )
                {
                    if ( *p >= 'a' && *p <= 'z' )
                    {
                        --p;
                    }
                    else
                    {
                        break;
                    }
                }
                filename_prefix = (uint32_t)(p - filename_start);
            }
            else if ( (*p >= 'A' && *p <= 'Z') && (*p1 >= 'A' && *p1 <= 'Z')
                      && (*(p-1) >= 'A' && *(p-1) <= 'Z') )
            {
                --p;
                while ( p > filename_start )
                {
                    if ( *p >= 'A' && *p <= 'Z' )
                    {
                        --p;
                    }
                    else
                    {
                        break;
                    }
                }
                filename_prefix = (uint32_t)(p - filename_start);
            }
        }

        p = path + path_len - 1;
        while ( p > filename_start )
        {
            if ( *p == '.' )
            {
                if ( strcmp(suffix, p) != 0 )
                {
                    if ( filename_lcp > 0 )
                        is_suffix_diff = 1;
                }
                else if ( *p1 == '\0' && filename_lcp == p - filename_start )
                {
                    is_basename_same = 1;
                }
                break;
            }
            --p;
        }
    }
    else
    {
        is_basename_same = strcmp(filename, filename_start) == 0;
    }

    p = path;
    p1 = dirname;
#if defined(_MSC_VER)
    while ( p < filename_start )
    {
        if ( *p1 == '\\' )
        {
            if ( *p == '\\' || *p == '/' )
            {
                ++dirname_lcp;
            }
            else
            {
                break;
            }
        }
        else if ( *p != *p1 )
        {
            break;
        }
        ++p;
        ++p1;
    }
#else
    while ( p < filename_start && *p == *p1 )
    {
        if ( *p == '/' )
        {
            ++dirname_lcp;
        }
        ++p;
        ++p1;
    }
#endif
    /**
     * e.g., dirname = "abc" , path = "abc/test.h"
     * p1 != dirname is to avoid such a case:
     * e.g., buffer name is "aaa.h", path is "/abc/def.h"
     */
#if defined(_MSC_VER)
    if ( *p1 == '\0' && p1 != dirname && (*p == '\\' || *p == '/') )
#else
    if ( *p1 == '\0' && p1 != dirname && *p == '/' )
#endif
    {
        ++dirname_lcp;
    }

    /* if dirname is empty, filename_start == path */
    is_dirname_same = filename_start - p == 1 || (*dirname == '\0' && filename_start == path) ;

    /* dirname/filename+suffix is the same as path */
    if ( is_basename_same && is_dirname_same )
    {
        return 0;
    }

    if ( filename_start == path && *dirname == '\0')
    {
        dirname_lcp = 1;
    }

    return (((filename_prefix + 1) << 24) | (dirname_lcp << 12) | (is_dirname_same << 11)
            | filename_lcp) + (is_suffix_diff << 2) - path_len;
}

static void delPatternContext(PyObject* obj)
{
    free(PyCapsule_GetPointer(obj, NULL));
}

static PyObject* fuzzyMatchC_initPattern(PyObject* self, PyObject* args)
{
    const char* pattern;
    Py_ssize_t pattern_len;

    if ( !PyArg_ParseTuple(args, "s#:initPattern", &pattern, &pattern_len) )
        return NULL;

    PatternContext* pCtxt = initPattern(pattern, (uint16_t)pattern_len);

    return PyCapsule_New(pCtxt, NULL, delPatternContext);
}

static PyObject* fuzzyMatchC_getWeight(PyObject* self, PyObject* args, PyObject* kwargs)
{
    const char* text;
    Py_ssize_t text_len;
    PyObject* py_patternCtxt;
    uint8_t is_name_only;
    static char* kwlist[] = {"text", "pattern", "is_name_only", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "s#Ob:getWeight", kwlist, &text,
                                      &text_len, &py_patternCtxt, &is_name_only) )
        return NULL;

    PatternContext* pCtxt = (PatternContext*)PyCapsule_GetPointer(py_patternCtxt, NULL);
    if ( !pCtxt )
        return NULL;

    return Py_BuildValue("f", getWeight(text, (uint16_t)text_len, pCtxt, is_name_only));
}

static PyObject* fuzzyMatchC_getHighlights(PyObject* self, PyObject* args, PyObject* kwargs)
{
    const char* text;
    Py_ssize_t text_len;
    PyObject* py_patternCtxt;
    uint8_t is_name_only;
    static char* kwlist[] = {"text", "pattern", "is_name_only", NULL};

    if ( !PyArg_ParseTupleAndKeywords(args, kwargs, "s#Ob:getHighlights", kwlist, &text,
                                      &text_len, &py_patternCtxt, &is_name_only) )
        return NULL;

    PatternContext* pCtxt = (PatternContext*)PyCapsule_GetPointer(py_patternCtxt, NULL);
    if ( !pCtxt )
        return NULL;

    HighlightGroup* pGroup = getHighlights(text, (uint16_t)text_len, pCtxt, is_name_only);
    if ( !pGroup )
        return NULL;

    PyObject* list = PyList_New(pGroup->end_index);
    uint16_t i;
    for ( i = 0; i < pGroup->end_index; ++i )
    {
        PyList_SetItem(list, i, Py_BuildValue("[H,H]", pGroup->positions[i].col, pGroup->positions[i].len));
    }
    free(pGroup);

    return list;
}

static PyMethodDef fuzzyMatchC_Methods[] =
{
    { "initPattern", (PyCFunction)fuzzyMatchC_initPattern, METH_VARARGS, "initialize the pattern." },
    { "getWeight", (PyCFunction)fuzzyMatchC_getWeight, METH_VARARGS | METH_KEYWORDS, "" },
    { "getHighlights", (PyCFunction)fuzzyMatchC_getHighlights, METH_VARARGS | METH_KEYWORDS, "" },
    { NULL, NULL, 0, NULL }
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef fuzzyMatchC_module =
{
    PyModuleDef_HEAD_INIT,
    "fuzzyMatchC",   /* name of module */
    "fuzzy match algorithm written in C.",
    -1,
    fuzzyMatchC_Methods
};

PyMODINIT_FUNC PyInit_fuzzyMatchC(void)
{
    PyObject* module = NULL;
    module = PyModule_Create(&fuzzyMatchC_module);
    if ( !module )
        return NULL;

    if ( PyModule_AddObject(module, "MIN_WEIGHT", Py_BuildValue("f", (float)MIN_WEIGHT)) )
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}

#else

PyMODINIT_FUNC initfuzzyMatchC(void)
{
    PyObject* module = NULL;
    module = Py_InitModule("fuzzyMatchC", fuzzyMatchC_Methods);
    if ( !module )
        return;

    if ( PyModule_AddObject(module, "MIN_WEIGHT", Py_BuildValue("f", (float)MIN_WEIGHT)) )
    {
        Py_DECREF(module);
        return;
    }
}

#endif

int main(int argc, const char* argv[])
{

    printf("%d\n", FM_BIT_LENGTH(0x2f00));

    return 0;
}

