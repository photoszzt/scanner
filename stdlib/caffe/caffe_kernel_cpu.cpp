#include "stdlib/caffe/caffe_kernel.h"

namespace scanner {

REGISTER_OP(Caffe).frame_input("caffe_frame").frame_output("caffe_output");

REGISTER_KERNEL(Caffe, CaffeKernel)
    .device(DeviceType::CPU)
    .batch()
    .num_devices(Kernel::UnlimitedDevices);
}
