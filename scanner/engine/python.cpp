#include "scanner/api/database.h"
#include "scanner/engine/op_info.h"
#include "scanner/engine/op_registry.h"
#include "scanner/util/common.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <thread>

namespace scanner {

namespace py = pybind11;

py::bytes default_machine_params_wrapper() {
  MachineParameters params = default_machine_params();
  proto::MachineParameters params_proto;
  params_proto.set_num_cpus(params.num_cpus);
  params_proto.set_num_load_workers(params.num_load_workers);
  params_proto.set_num_save_workers(params.num_save_workers);
  for (auto gpu_id : params.gpu_ids) {
    params_proto.add_gpu_ids(gpu_id);
  }

  std::string output;
  bool success = params_proto.SerializeToString(&output);
  LOG_IF(FATAL, !success) << "Failed to serialize machine params";
  return py::bytes(output);
}

proto::Result start_master_wrapper(Database& db, const std::string& port, bool watchdog) {
  return db.start_master(default_machine_params(), port, watchdog);
}

proto::Result start_worker_wrapper(Database& db, const std::string& params_s,
                                   const std::string& port, bool watchdog) {
  proto::MachineParameters params_proto;
  params_proto.ParseFromString(params_s);
  MachineParameters params;
  params.num_cpus = params_proto.num_cpus();
  params.num_load_workers = params_proto.num_load_workers();
  params.num_save_workers = params_proto.num_save_workers();
  for (auto gpu_id : params_proto.gpu_ids()) {
    params.gpu_ids.push_back(gpu_id);
  }

  return db.start_worker(params, port, watchdog);
}

std::vector<FailedVideo> ingest_videos_wrapper(Database& db, std::vector<std::string> table_names,
                               std::vector<std::string> paths) {
  py::gil_scoped_release release;
  std::vector<FailedVideo> failed_videos;
  db.ingest_videos(table_names, paths, failed_videos);
  return failed_videos;
}

Result wait_for_server_shutdown_wrapper(Database& db) {
  py::gil_scoped_release release;
  return db.wait_for_server_shutdown();
}

Result new_table_wrapper(Database& db, const std::string& name,
                         std::vector<std::string> columns, std::vector<std::vector<std::string>> rows) {
  py::gil_scoped_release release;
  return db.new_table(name, columns, rows);
}

PYBIND11_MODULE(_python, m) {
  m.doc() = "Scanner C library";
  m.attr("__name__") = "scannerpy._python";
  py::class_<Database>(m, "Database")
      .def(py::init<storehouse::StorageConfig*, const std::string&, const std::string&>())
      .def("ingest_videos", &Database::ingest_videos);

  py::class_<FailedVideo>(m, "FailedVideo")
      .def_readonly("path", &FailedVideo::path)
      .def_readonly("message", &FailedVideo::message);

  py::class_<proto::Result>(m, "Result")
      .def("success", &proto::Result::success)
      .def("msg", &proto::Result::msg);

  m.def("start_master", &start_master_wrapper);
  m.def("start_worker", &start_worker_wrapper);
  m.def("ingest_videos", &ingest_videos_wrapper);
  m.def("wait_for_server_shutdown", &wait_for_server_shutdown_wrapper);
  m.def("default_machine_params", &default_machine_params_wrapper);
  m.def("new_table", &new_table_wrapper);
}
}
