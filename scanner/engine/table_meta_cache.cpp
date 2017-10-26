/* Copyright 2017 Carnegie Mellon University
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

#include "scanner/engine/table_meta_cache.h"

namespace scanner {
namespace internal {

TableMetaCache::TableMetaCache(storehouse::StorageBackend* storage,
                               const DatabaseMetadata& meta)
  : storage_(storage), meta_(meta) {}

const TableMetadata& TableMetaCache::at(const std::string& table_name) const {
  i32 table_id = meta_.get_table_id(table_name);
  memoized_read(table_id);
  std::lock_guard<std::mutex> lock(lock_);
  return cache_.at(table_id);
}

const TableMetadata& TableMetaCache::at(i32 table_id) const {
  memoized_read(table_id);
  std::lock_guard<std::mutex> lock(lock_);
  return cache_.at(table_id);
}

bool TableMetaCache::exists(const std::string& table_name) const {
  return meta_.has_table(table_name);
}

bool TableMetaCache::exists(i32 table_id) const {
  return meta_.has_table(table_id);
}

void TableMetaCache::update(const TableMetadata& meta) {
  std::lock_guard<std::mutex> lock(lock_);
  i32 table_id = meta_.get_table_id(meta.name());
  cache_[table_id] = meta;
}


void TableMetaCache::memoized_read(const std::string& table_name) const {
  memoized_read(meta_.get_table_id(table_name));
}

void TableMetaCache::memoized_read(i32 table_id) const {
  bool b;
  {
    std::lock_guard<std::mutex> lock(lock_);
    b = cache_.count(table_id) == 0 && meta_.has_table(table_id);
  }
  if (b) {
    std::string table_path = TableMetadata::descriptor_path(table_id);
    TableMetadata meta = read_table_metadata(storage_, table_path);
    std::lock_guard<std::mutex> lock(lock_);
    cache_.insert({table_id, meta});
  }
}

}
}
