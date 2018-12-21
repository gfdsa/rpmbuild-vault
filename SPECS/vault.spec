%define debug_package %{nil}

Name:           vault
Version:        1.0.0
Release:        2%{dist}
Summary:        A tool for managing secrets
Group:          Applications/Internet
License:        Mozilla Public License 2.0
URL:            https://www.vaultproject.io/
%ifarch x86_64 amd64
Source0:        https://releases.hashicorp.com/%{name}/%{version}/%{name}_%{version}_linux_amd64.zip
%else
Source0:        https://releases.hashicorp.com/%{name}/%{version}/%{name}_%{version}_linux_386.zip
%endif
Source1:        %{name}.hcl
Source2:        %{name}.init
Source3:        %{name}.logrotate
Source4:        %{name}.sysconfig
Source5:        %{name}.tmpfiles
Source6:        %{name}.service
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if ( 0%{?fedora} && 0%{?fedora} >= 15)
BuildRequires: systemd-units
%endif

%description
Vault is a tool for securely accessing secrets. A secret is anything that you want
to tightly control access to, such as API keys, passwords, certificates, and more.
Vault provides a unified interface to any secret, while providing tight access
control and recording a detailed audit log.

%prep
%setup -c -q
%build
%install
%{__install} -d -m 0755 %{buildroot}%{_sbindir} \
                        %{buildroot}%{_sysconfdir}/%{name} \
                        %{buildroot}%{_sysconfdir}/logrotate.d \
                        %{buildroot}%{_localstatedir}/{lib,log,run}/%{name}

%{__install} -m 0600 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -m 0755 %{_builddir}/%{name}-%{version}/%{name} %{buildroot}%{_sbindir}

%if ( 0%{?fedora} && 0%{?fedora} <= 15) || (0%{?rhel} && 0%{?rhel} <= 6)
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/rc.d/init.d \
                        %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -m 0755 %{SOURCE2} %{buildroot}%{_sysconfdir}/rc.d/init.d/%{name}
%else
%{__install} -d -m 755 %{buildroot}%{_prefix}/lib/tmpfiles.d %{buildroot}/%{_unitdir}
%{__install} -m 644 %{SOURCE5} %{buildroot}%{_prefix}/lib/tmpfiles.d/%{name}.conf
%{__install} -m 644 %{SOURCE6} %{buildroot}%{_unitdir}/%{name}.service
%endif

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -s /sbin/nologin \
    -d %{_localstatedir}/lib/%{name} -c "RPM Created Vault User" %{name}

%if ( 0%{?fedora} && 0%{?fedora} <= 15) || (0%{?rhel} && 0%{?rhel} <= 6)

%post
/sbin/chkconfig --add %{name}

%preun
/sbin/service %{name} stop > /dev/null 2>&1
/sbin/chkconfig --del %{name}

%else

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,vault,vault,-)
%attr(-,root,root) %{_sbindir}/%{name}
%attr(-,root,root) %{_sysconfdir}/logrotate.d/%{name}
%if ( 0%{?fedora} && 0%{?fedora} <= 15) || (0%{?rhel} && 0%{?rhel} <= 6)
%attr(-,root,root) %{_sysconfdir}/rc.d/init.d/%{name}
%attr(-,root,root) %{_sysconfdir}/sysconfig/%{name}
%else
%attr(-,root,root) %{_prefix}/lib/tmpfiles.d/%{name}.conf
%attr(-,root,root) %{_unitdir}/%{name}.service
%endif
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.*
%{_localstatedir}/lib/%{name}
%{_localstatedir}/log/%{name}
%{_localstatedir}/run/%{name}

%changelog
* Fri Dec 21 2018 Michael Tabolsky <gfdsa@gfdsa.org> - 1.0.0-2
- Added systemd scriptlets

* Fri Dec 14 2018 Michael Tabolsky <gfdsa@gfdsa.org> - 1.0.0-1
- Bumped vault to 1.0
- Modernized some stuff

* Tue Mar 27 2018 Taylor Kimball <tkimball@linuxhq.org> - 0.9.6-1
- Updated to 0.9.6
- Add vault user to runas

* Mon Feb 12 2018 Taylor Kibmall <tkimball@linuxhq.org> - 0.9.3-1
- Updated to 0.9.3

* Mon May 02 2016 Taylor Kimball <tkimball@linuxhq.org> - 0.5.2-1
- Initial build.
