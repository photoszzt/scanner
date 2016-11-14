/* Copyright 2016 Carnegie Mellon University
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once

#include "scanner/evaluators/types.pb.h"

#include <vector>

namespace scanner {

template <typename T>
void serialize_proto_vector(const std::vector<T>& elements, u8*& buffer,
                            size_t& size) {
  size = sizeof(size_t);
  for (auto& e : elements) {
    size += e.ByteSize() + sizeof(i32);
  }
  buffer = new u8[size];

  u8* buf = buffer;
  *((size_t*)buf) = elements.size();
  buf += sizeof(size_t);
  for (size_t i = 0; i < elements.size(); ++i) {
    const T& e = elements[i];
    i32 element_size = e.ByteSize();
    *((i32*)buf) = element_size;
    buf += sizeof(i32);
    e.SerializeToArray(buf, element_size);
    buf += element_size;
  }
}

inline void serialize_bbox_vector(const std::vector<BoundingBox>& bboxes,
                                  u8*& buffer, size_t& size) {
  serialize_proto_vector(bboxes, buffer, size);
}

inline void serialize_decode_args(const DecodeArgs& args, u8*& buffer,
                                  size_t& size) {
  size = args.ByteSize();
  buffer = new u8[size];
  args.SerializeToArray(buffer, size);
}

inline DecodeArgs deserialize_decode_args(const u8* buffer, size_t size) {
  DecodeArgs args;
  args.ParseFromArray(buffer, size);
  return args;
}

inline void serialize_image_decode_args(const ImageDecodeArgs& args,
                                        u8*& buffer, size_t& size) {
  size = args.ByteSize();
  buffer = new u8[size];
  args.SerializeToArray(buffer, size);
}

inline ImageDecodeArgs deserialize_image_decode_args(const u8* buffer,
                                                     size_t size) {
  ImageDecodeArgs args;
  args.ParseFromArray(buffer, size);
  return args;
}
}
