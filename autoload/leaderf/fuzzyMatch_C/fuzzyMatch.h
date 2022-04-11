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

#ifndef FUZZYMATCH_H_
#define FUZZYMATCH_H_

#include "mystdint.h"

#define MIN_WEIGHT (-1000000.0f)

typedef struct PatternContext
{
    const char* pattern;
    int64_t pattern_mask[256];
    uint16_t pattern_len;
    uint16_t actual_pattern_len;
    uint8_t is_lower;
}PatternContext;

typedef struct HighlightPos
{
    uint16_t col;
    uint16_t len;
}HighlightPos;

typedef struct HighlightGroup
{
    float score;
    uint16_t beg;
    uint16_t end;
    HighlightPos positions[64];
    uint16_t end_index;
}HighlightGroup;

#ifdef __cplusplus
extern "C" {
#endif

PatternContext* initPattern(const char* pattern, uint16_t pattern_len);

float getWeight(const char* text, uint16_t text_len, PatternContext* pPattern_ctxt, uint8_t is_name_only);

HighlightGroup* getHighlights(const char* text, uint16_t text_len, PatternContext* pPattern_ctxt, uint8_t is_name_only);

uint32_t getPathWeight(const char* filename,
                       const char* suffix,
                       const char* dirname,
                       const char* path, uint32_t path_len);

#ifdef __cplusplus
}
#endif

#endif
