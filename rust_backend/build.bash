
export ANDROID_NDK_HOME=~/Android/Sdk/ndk/25.1.8937393
export PATH=$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH

cargo build --target aarch64-linux-android --release \
  -Z build-std=std,panic_abort
