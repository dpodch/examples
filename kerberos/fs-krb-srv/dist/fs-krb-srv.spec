%define name			fs-krb-srv
%define version_major	1
%define version_minor	2
%define version_patch	1
%define	version_build	3

%define debug_package %{nil}

%define service_dir usr/lib/systemd/system
%define install_dir opt/forsys/fs-krb-srv
%define keys_dir etc/fskeys


%define is_astralinux_16 %(grep -w -q "1.6" /etc/astra_version && echo 1 || echo 0)

Summary:	The Forward Systems daemon

Name:		%{name}
Version:	%{version_major}.%{version_minor}.%{version_patch}
Release:	%{version_build}%{?dist}
License:	GPL
URL:		http://forsys.ru
Group:		System Environment/Libraries
Source:		%{name}-%{version}.tgz
BuildRoot:	%_tmppath/%name-%version-%release-root
Requires:   python2, python-kerberos
Provides:	%{name} = %{version}

%description
The Forward Systems daemon

%if %is_astralinux_16
 %define AstraLinuxRequires_fs-krb-srv: python, python-kerberos, krb5-user
%endif

%prep
%setup -q -n %{name}-%{version}

%build

%install

%__rm -rf %buildroot

# install systemd unit file
mkdir -p %{buildroot}/%{service_dir}
%__cp -f systemd/*.service %{buildroot}/%{service_dir}/

#doc
mkdir -p %{buildroot}/%{keys_dir}/
mkdir -p %{buildroot}/%{install_dir}/
pwd
%__cp -f src/fs-krb-srv.py src/env.file %{buildroot}/%{install_dir}/
%__cp -f src/*.sh %{buildroot}/%{install_dir}/
%__cp -f src/*.txt %{buildroot}/%{install_dir}/

%post
# systemctl daemon-reload

%postun

%clean
if [ "%buildroot" != "/" ] ; then
	%__rm -rf %buildroot
fi


%files
%defattr(-,root,root,-)
/%{install_dir}/*
/%{keys_dir}/
%attr(644,root,root) /%{service_dir}/*.service

%changelog

* Tue Jul 21 2020 Denis Podchernyaev <denis@forsys.ru> <1.2.1>
-  [bug 21222] added check for key creation

* Tue Jul 21 2020 Denis Podchernyaev <denis@forsys.ru> <1.1.4>
-  [bug 21222] kerberos get ticket implemented

* Mon Jul 20 2020 Denis Podchernyaev <denis@forsys.ru> <1.1.0>
-  [bug 21222] fixed restart service for update ticket

* Sat Jul 20 2020 Denis Podchernyaev <denis@forsys.ru> <1.0.0>
-  init version
