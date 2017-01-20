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

#include "scanner/engine/kernel_registry.h"

namespace scanner {

void EvaluatorRegistry::add_evaluator(const std::string &name,
                                      EvaluatorInfo *info) {
  evaluators_.insert({name, info});
}

EvaluatorFactory* EvaluatorRegistry::get_kernel(const std::string &name) const {
  return evaluators_.at(name);
}

EvaluatorRegistry* get_evaluator_registry() {
  static EvaluatorRegistry* registry = new EvaluatorRegistry;
  return registry;
}
}