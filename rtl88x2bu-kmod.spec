# Build an akmod by default. An explicit "kernels" definition makes kmodtool
# build kernel-versioned kmod packages instead.
%global buildforkernels akmod

%global debug_package %{nil}

%global kmod_name rtl88x2bu
%global module_name 88x2bu
%global repo_name RTL88x2BU-Linux-Driver
%global commit 0026128fa37398416bc14a3220e85596b84cf6c7
%global commitdate 20260905
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           %{kmod_name}-kmod
Version:        0.%{commitdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Realtek RTL8812BU/RTL8822BU USB Wi-Fi kernel module

License:        GPL-2.0-only
URL:            https://github.com/RinCat/RTL88x2BU-Linux-Driver
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{commit}.tar.gz
Source1:        rtw8822bu.conf

%global AkmodsBuildRequires gcc, make, elfutils-libelf-devel, xz, bc
BuildRequires:  kmodtool
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-rpm-macros

# kmodtool generates akmod/kmod subpackages and install/check helper macros.
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
Out-of-tree Realtek RTL8812BU and RTL8822BU USB Wi-Fi kernel module.


%package -n %{pkg_kmod_name}-common
Summary:        Common files for %{kmod_name} kernel modules
BuildArch:      noarch


%description -n %{pkg_kmod_name}-common
Common modprobe configuration for the packaged %{kmod_name} kernel module.

%prep
# Error out if kmodtool generated a diagnostic macro.
%{?kmodtool_check}

# Print generated package template for build logs/debugging.
kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c

for kernel_version in %{?kernel_versions}; do
    cp -a %{repo_name}-%{commit} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    ksrc=${kernel_version##*___}
    make V=1 %{?_smp_mflags} \
        -C "_kmod_build_${kver}" \
        KVER="${kver}" \
        KSRC="${ksrc}" \
        modules
done


%install
install -Dpm0644 %{SOURCE1} \
    %{buildroot}%{_modprobedir}/rtw8822bu.conf

for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    moddir=%{buildroot}%{kmodinstdir_prefix}/${kver}/%{kmodinstdir_postfix}
    install -d -m 0755 "${moddir}"
    install -Dpm0644 "_kmod_build_${kver}/%{module_name}.ko" \
        "${moddir}/%{module_name}.ko"
done
%{?akmod_install}


%files -n %{pkg_kmod_name}-common
%config(noreplace) %{_modprobedir}/rtw8822bu.conf


%changelog
