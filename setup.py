import os.path as osp
import os

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

ROOT = osp.dirname(osp.abspath(__file__))


def _nvcc_arch_flags():
    """Build CUDA arch flags from env; default avoids deprecated sm_70 on CUDA 13."""
    arch_list = os.environ.get("MEGASAM_CUDA_ARCHES") or os.environ.get("TORCH_CUDA_ARCH_LIST")
    if arch_list:
        entries = [x.strip().replace("+PTX", "") for x in arch_list.replace(";", ",").split(",") if x.strip()]
        flags = []
        for e in entries:
            major_minor = e.split(".")
            if len(major_minor) == 1:
                sm = f"{major_minor[0]}0"
            else:
                sm = f"{major_minor[0]}{major_minor[1]}"
            flags.append(f"-gencode=arch=compute_{sm},code=sm_{sm}")
        if flags:
            return flags

    return [
        "-gencode=arch=compute_75,code=sm_75",
        "-gencode=arch=compute_80,code=sm_80",
        "-gencode=arch=compute_86,code=sm_86",
        "-gencode=arch=compute_89,code=sm_89",
        "-gencode=arch=compute_90,code=sm_90",
    ]

setup(
    name='droid_backends',
    ext_modules=[
        CUDAExtension(
            'droid_backends',
            include_dirs=[osp.join(ROOT, 'thirdparty/eigen')],
            sources=[
                'src/droid.cpp',
                'src/droid_kernels.cu',
                'src/correlation_kernels.cu',
                'src/altcorr_kernel.cu',
            ],
            extra_compile_args={
                'cxx': ['-O3'],
                'nvcc': [
                    '-O3',
                    '-diag-suppress=20011',
                    '-diag-suppress=20014',
                ] + _nvcc_arch_flags(),
            },
        ),
    ],
    cmdclass={'build_ext': BuildExtension},
)

setup(
    name='lietorch',
    version='0.2',
    description='Lie Groups for PyTorch',
    packages=['lietorch'],
    package_dir={'': 'thirdparty/lietorch'},
    ext_modules=[
        CUDAExtension(
            'lietorch_backends',
            include_dirs=[
                osp.join(ROOT, 'thirdparty/lietorch/lietorch/include'),
                osp.join(ROOT, 'thirdparty/eigen'),
            ],
            sources=[
                'thirdparty/lietorch/lietorch/src/lietorch.cpp',
                'thirdparty/lietorch/lietorch/src/lietorch_gpu.cu',
                'thirdparty/lietorch/lietorch/src/lietorch_cpu.cpp',
            ],
            extra_compile_args={
                'cxx': ['-O2'],
                'nvcc': [
                    '-O2',
                    '-diag-suppress=20011',
                    '-diag-suppress=20014',
                ] + _nvcc_arch_flags(),
            },
        ),
    ],
    cmdclass={'build_ext': BuildExtension},
)
