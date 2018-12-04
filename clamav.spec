# TODO:
# - Make freshclam package (script and daemon)
# - restart amavis in triggers if group membership was modified?
#
# Conditional build:
%bcond_without	milter		# milter interface subpackage
%if "%{pld_release}" == "ac"
%bcond_with	llvm		# LLVM support
%else
%bcond_without	llvm		# LLVM support
%endif

%ifarch x32
%undefine with_llvm
%endif

%bcond_with	system_llvm

Summary:	An anti-virus utility for Unix
Summary(pl.UTF-8):	Narzędzie antywirusowe dla Uniksów
Name:		clamav
Version:	0.101.0
Release:	1
License:	GPL v2+
Group:		Daemons
Source0:	http://www.clamav.net/downloads/production/%{name}-%{version}.tar.gz
# Source0-md5:	47c36d13ac814b9e29ed6f5fc1691373
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-milter.init
Source4:	%{name}-cron-updatedb
Source5:	%{name}.logrotate
Source8:	%{name}-post-updatedb
Source9:	%{name}-milter.sysconfig
Source10:	%{name}.tmpfiles
Source11:	clamd.service
Source12:	cronjob-clamav.timer
Source13:	cronjob-clamav.service.in
Patch0:		%{name}-pld_config.patch
Patch1:		%{name}-nolibs.patch
%if "%{pld_release}" == "ac"
Patch2:		am-nosilentrules.patch
%endif
Patch3:		ac2.68.patch
Patch4:		%{name}-openssl.patch
Patch5:		%{name}-major.patch
Patch6:		x32.patch
URL:		http://www.clamav.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	check-devel
BuildRequires:	curl-devel
BuildRequires:	gmp-devel
BuildRequires:	libltdl-devel
%{?with_milter:BuildRequires:	libmilter-devel}
BuildRequires:	libstdc++-devel >= 5:3.4
BuildRequires:	libtool
%{?with_milter:BuildRequires:	libwrap-devel}
%{?with_llvm:%{?with_system_llvm:BuildRequires:	llvm-devel < 3.7}}
BuildRequires:	ncurses-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(postun,pre):	/usr/sbin/usermod
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 38
Requires(triggerpostun):	sed >= 4.0
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires:	/usr/sbin/usermod
Requires:	rc-scripts >= 0.4.1.23
Suggests:	clamav-database
Suggests:	cronjobs
Provides:	group(clamav)
Provides:	user(clamav)
Conflicts:	logrotate < 3.7-4
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Clam AntiVirus is an open source anti-virus toolkit for UNIX, designed
especially for e-mail scanning on mail gateways. It provides a number
of utilities including a flexible and scalable multi-threaded daemon,
a command line scanner and advanced tool for automatic database
updates. The core of the package is an anti-virus engine available in
a form of shared library.

Here is a list of the main features:
- command-line scanner
- fast, multi-threaded daemon with support for on-access scanning
- milter interface for sendmail
- advanced database updater with support for scripted updates and
  digital signatures
- virus scanner C library
- on-access scanning (Linux® and FreeBSD®)
- virus database updated multiple times per day (see home page for
  total number of signatures)
- built-in support for various archive formats, including Zip, RAR,
  Tar, Gzip, Bzip2, OLE2, Cabinet, CHM, BinHex, SIS and others
- built-in support for almost all mail file formats
- built-in support for ELF executables and Portable Executable files
  compressed with UPX, FSG, Petite, NsPack, wwpack32, MEW, Upack and
  obfuscated with SUE, Y0da Cryptor and others
- built-in support for popular document formats including MS Office
  and MacOffice files, HTML, RTF and PDF

%description -l pl.UTF-8
Clam Antivirus jest potężnym skanerem antywirusowym dla systemów
uniksowych. Wspiera on AMaViSa, skompresowane pliki, skanowanie
"on-access" i posiada system bezpiecznej, automatycznej aktualizacji.
Baza wirusów zawiera ponad 90000 sygnatur. Skaner jest wielowątkowy,
napisany w C i zgodny z POSIXem.

%package libs
Summary:	Shared libraries for clamav
Summary(pl.UTF-8):	Biblioteki dzielone clamav
Group:		Libraries

%description libs
Shared libraries for clamav.

%description libs -l pl.UTF-8
Biblioteki dzielone clamav.

%package milter
Summary:	ClamAV filter using milter interface
Summary(pl.UTF-8):	Filtr ClamAV korzystający z interfejsu milter
Group:		Daemons
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	postfix
#Requires:	sendmail >= 8.11
Requires:	tcp_wrappers

%description milter
ClamAV sendmail filter using MILTER interface.

%description milter -l pl.UTF-8
Filtr ClamAV dla sendmaila korzystający z interfejsu MILTER.

%package devel
Summary:	clamav - Development header files and libraries
Summary(pl.UTF-8):	clamav - Pliki nagłówkowe i biblioteki dla programistów
Group:		Development/Libraries
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires:	bzip2-devel
Requires:	curl-devel
Requires:	gmp-devel
Requires:	openssl-devel
Requires:	zlib-devel

%description devel
This package contains the development header files and libraries
necessary to develop clamav client applications.

%description devel -l pl.UTF-8
Pliki nagłówkowe i biblioteki konieczne do kompilacji aplikacji
klienckich clamav.

%package static
Summary:	clamav static libraries
Summary(pl.UTF-8):	Biblioteki statyczne clamav
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
clamav static libraries.

%description static -l pl.UTF-8
Biblioteki statyczne clamav.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%if "%{pld_release}" == "ac"
%patch2 -p1
%endif
%if "%{pld_release}" != "ac"
%patch3 -p1
%endif
#%patch4 -p1
%patch5 -p1
%patch6 -p1

%build
export CFLAGS="%{rpmcflags} -Wall -W -Wmissing-prototypes -Wmissing-declarations -std=gnu99"
export CXXFLAGS="%{rpmcxxflags} -std=gnu++98"
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-zlib-vcheck \
	--disable-silent-rules \
	--disable-clamav \
	--enable-clamdtop \
	%{?with_llvm:--enable-llvm %{!?with_system_llvm:--with-system-llvm=no}} \
	%{?with_milter:--enable-milter} \
	--with-dbdir=/var/lib/%{name} \
	--with-no-cache \
	--with-ltdl-include=%{_includedir} \
	--with-ltdl-lib=%{_libdir}

%{__make} \
	LIBTOOL=%{_bindir}/libtool

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{cron.d,logrotate.d,rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT%{_var}/{log,spool/clamav,lib/clamav} \
	$RPM_BUILD_ROOT%{systemdtmpfilesdir} \
	$RPM_BUILD_ROOT%{systemdunitdir}

%{__make} install \
	LIBTOOL=%{_bindir}/libtool \
	DESTDIR=$RPM_BUILD_ROOT
%{!?with_milter:rm -f $RPM_BUILD_ROOT%{_mandir}/man8/clamav-milter.8*}

cat <<'EOF' >$RPM_BUILD_ROOT/etc/cron.d/%{name}
5 * * * *	root	%{_sbindir}/clamav-cron-updatedb
EOF

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamd
%if %{with milter}
install -p %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamav-milter
cp -p %{SOURCE9} $RPM_BUILD_ROOT/etc/sysconfig/clamav-milter
%endif
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/clamd
install -p %{SOURCE4} $RPM_BUILD_ROOT%{_sbindir}/clamav-cron-updatedb
for i in $RPM_BUILD_ROOT%{_sysconfdir}/*.conf.sample; do
	mv $i ${i%%.sample}
done
cp -p %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

install -p %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}

cp -p %{SOURCE10} $RPM_BUILD_ROOT%{systemdtmpfilesdir}/%{name}.conf

cp -p %{SOURCE11} $RPM_BUILD_ROOT%{systemdunitdir}
cp -p %{SOURCE12} $RPM_BUILD_ROOT%{systemdunitdir}/cronjob-%{name}.timer
sed -e's#@sbindir@#%{_sbindir}#' <  %{SOURCE13} > $RPM_BUILD_ROOT%{systemdunitdir}/cronjob-%{name}.service

# NOTE: clamd uses sane rights to it's clamd.pid file
# So better keep it dir
# If it is fixed use of dir will be unecesary
install -d $RPM_BUILD_ROOT/var/run/%{name}

:> $RPM_BUILD_ROOT/var/log/freshclam.log

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- amavis-ng
%addusertogroup -q clamav amavis

%triggerin -- amavisd-new
%addusertogroup -q clamav amavis

%triggerin -- amavisd
%addusertogroup -q clamav amavis

%pre
%groupadd -g 43 clamav
%useradd -u 43 -d /tmp -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav

%post
/sbin/chkconfig --add clamd
%service clamd restart "Clam Antivirus daemon"
touch /var/log/freshclam.log
chown clamav:root /var/log/freshclam.log
chmod 640 /var/log/freshclam.log
%systemd_post clamd.service cronjob-clamav.timer

%preun
if [ "$1" = "0" ]; then
	%service clamd stop
	/sbin/chkconfig --del clamd
fi
%systemd_preun clamd.service cronjob-clamav.timer

%postun
if [ "$1" = "0" ]; then
	%userremove clamav
	%groupremove clamav
fi
%systemd_reload

%triggerpostun -- %{name} < 0.80
if [ -f /etc/clamav.conf.rpmsave ]; then
	echo "Renaming config to new name /etc/clamd.conf"
	mv -f /etc/clamd.conf /etc/clamd.conf.rpmnew
	mv -f /etc/clamav.conf.rpmsave /etc/clamd.conf
	echo "Changing config location in freshclam config"
	%{__sed} -i -e 's/clamav.conf/clamd.conf/' /etc/freshclam.conf
fi

%triggerpostun -- %{name} < 0.90-0.rc2.0.10
%{__cp} -f /etc/clamd.conf{,.rpmsave}
%{__sed} -i -e '
		s,^LogSyslog$,& yes,
		s,^FixStaleSocket$,& yes,
		s,^AllowSupplementaryGroups$,& yes,
		s,^ClamukoScanOnOpen$,& yes,
		s,^ClamukoScanOnClose$,& yes,
		s,^ClamukoScanOnExec$,& yes,
		s,^LogTime$,& yes,
		s,^ScanPE$,& yes,
' /etc/clamd.conf
%banner -e %{name}-0.90 <<EOF
ClamAV config was automatically upgraded to 0.90 format. You should review it
that it's still valid.
EOF
#'
# unfortunately clamd has no configcheck option so we just have to start it
# once again after config was broken after upgrade
touch /var/lock/subsys/clamd
%service -q clamd restart

%triggerpostun -- %{name} < 0.97.7-4
%systemd_trigger clamd.service

%triggerpostun -- %{name} < 0.99.2-2
%systemd_service_enable cronjob-clamav.timer

%post milter
/sbin/chkconfig --add clamav-milter
%service clamav-milter restart "Clam Antivirus daemon"

%preun milter
if [ "$1" = "0" ]; then
	%service clamav-milter stop
	/sbin/chkconfig --del clamav-milter
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc ChangeLog.md NEWS.md README.md
%attr(755,root,root) %{_bindir}/clambc
%attr(755,root,root) %{_bindir}/clamdscan
%attr(755,root,root) %{_bindir}/clamdtop
%attr(755,root,root) %{_bindir}/clamscan
%attr(755,root,root) %{_bindir}/clamsubmit
%attr(755,root,root) %{_bindir}/freshclam
%attr(755,root,root) %{_bindir}/sigtool
%attr(755,root,root) %{_bindir}/clamconf
%attr(755,root,root) %{_sbindir}/clamd
%attr(755,root,root) %{_sbindir}/clamav-cron-updatedb
%attr(755,root,root) %{_sbindir}/clamav-post-updatedb
%{systemdtmpfilesdir}/%{name}.conf
%{systemdunitdir}/clamav-daemon.service
%{systemdunitdir}/clamav-daemon.socket
%{systemdunitdir}/clamav-freshclam.service
%{systemdunitdir}/clamd.service
%{systemdunitdir}/cronjob-clamav.service
%{systemdunitdir}/cronjob-clamav.timer
%attr(755,clamav,root) %dir /var/lib/%{name}
%attr(640,clamav,root) %ghost /var/log/freshclam.log
%attr(750,clamav,clamav) %dir /var/run/%{name}

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/clamd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/freshclam.conf

%attr(754,root,root) /etc/rc.d/init.d/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/clamav
%{_mandir}/man1/*
%{_mandir}/man5/clamd*
%{_mandir}/man5/freshclam*
%{_mandir}/man8/clamd*

%if %{with milter}
%files milter
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/clamav-milter
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/clamav-milter.conf
%attr(754,root,root) /etc/rc.d/init.d/clamav-milter
#%attr(755,root,root) %{_sysconfdir}/cron.daily/clamav-milter
#%attr(755,root,root) %{_sysconfdir}/log.d/scripts/services/clamav-milter
#%{_sysconfdir}/log.d/conf/services/clamav-milter.conf
%attr(755,root,root) %{_sbindir}/clamav-milter
%{_mandir}/man5/clamav-milter*
%{_mandir}/man8/clamav-milter.8*
%attr(700,clamav,clamav) /var/spool/clamav
%endif

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libclamav.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclamav.so.9
%attr(755,root,root) %{_libdir}/libclammspack.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclammspack.so.0
%attr(755,root,root) %{_libdir}/libclamunrar.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclamunrar.so.9
%attr(755,root,root) %{_libdir}/libclamunrar_iface.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libclamunrar_iface.so.9

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/clamav-config
%attr(755,root,root) %{_libdir}/libclamav.so
%attr(755,root,root) %{_libdir}/libclammspack.so
%attr(755,root,root) %{_libdir}/libclamunrar.so
%attr(755,root,root) %{_libdir}/libclamunrar_iface.so
%{_libdir}/libclamav.la
%{_libdir}/libclammspack.la
%{_libdir}/libclamunrar.la
%{_libdir}/libclamunrar_iface.la
%{_includedir}/clamav.h
%{_pkgconfigdir}/libclamav.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libclamav.a
%{_libdir}/libclammspack.a
%{_libdir}/libclamunrar.a
%{_libdir}/libclamunrar_iface.a
