# TODO:
# - Make freshclam package (script and daemon)
#
# Conditional build:
%bcond_without	milter		# build without milter subpackage
%bcond_with	curl		# enable curl support
#
Summary:	An anti-virus utility for Unix
Summary(pl.UTF-8):	Narzędzie antywirusowe dla Uniksów
Name:		clamav
Version:	0.90.3
Release:	1
Epoch:		0
License:	GPL
Group:		Applications
Source0:	http://dl.sourceforge.net/clamav/%{name}-%{version}.tar.gz
# Source0-md5:	d42ccf7a32daeb7c7cc3c8c23a7793ea
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-milter.init
Source4:	%{name}-cron-updatedb
Source5:	%{name}.logrotate
Source8:	%{name}-post-updatedb
Source9:	%{name}-milter.sysconfig
Patch0:		%{name}-pld_config.patch
Patch1:		%{name}-no_auto_libwrap.patch
Patch2:		%{name}-nolibs.patch
Patch3:		%{name}-find_milter.patch
URL:		http://www.clamav.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	bzip2-devel
%{?with_curl:BuildRequires:	curl-devel}
BuildRequires:	gmp-devel
%{?with_milter:BuildRequires:	libmilter-devel}
BuildRequires:	libtool
%{?with_milter:BuildRequires:	libwrap-devel}
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(postun,pre):	/usr/sbin/usermod
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(triggerpostun):	sed >= 4.0
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
Requires:	/usr/sbin/usermod
Requires:	bc
Requires:	rc-scripts
Provides:	group(clamav)
Provides:	user(clamav)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Clam Antivirus is a powerful anti-virus scanner for Unix. It supports
AMaViS, compressed files, on-access scanning and includes a program
for auto-updating with support for digital signatures. The virus
database has over 90000 viruses, worms and trojans signatures. The
scanner is multithreaded, written in C, and POSIX compliant.

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
Requires:	sendmail >= 8.11
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
Requires:	gmp-devel
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
%setup -q %{?_rc:-n %{name}-%{version}%{_rc}}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--disable-clamav \
	%{!?with_curl:--without-libcurl} \
	%{?with_milter:--enable-milter} \
	--with-dbdir=/var/lib/%{name}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{cron.d,logrotate.d,rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT%{_var}/{log,spool/clamav}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
%{!?with_milter:rm -f $RPM_BUILD_ROOT%{_mandir}/man8/clamav-milter.8*}

cat <<'EOF' >$RPM_BUILD_ROOT/etc/cron.d/%{name}
5 * * * *	root	%{_sbindir}/clamav-cron-updatedb
EOF

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamd
%if %{with milter}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamav-milter
install %{SOURCE9} $RPM_BUILD_ROOT/etc/sysconfig/clamav-milter
%endif
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/clamd
install %{SOURCE4} $RPM_BUILD_ROOT%{_sbindir}/clamav-cron-updatedb
install etc/*.conf $RPM_BUILD_ROOT%{_sysconfdir}
install %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

install %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}

# NOTE: clamd uses sane rights to it's clamd.pid file
# So better keep it dir
# If it is fixed use of dir will be unecesary
install -d $RPM_BUILD_ROOT/var/run/%{name}

:> $RPM_BUILD_ROOT/var/log/freshclam.log

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- amavis-ng
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	echo "Adding clamav to amavis group GID=$AMAVIS"
	/usr/sbin/usermod -G amavis clamav 1>&2 > /dev/null
fi

%triggerin -- amavisd-new
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	echo "Adding clamav to amavis group GID=$AMAVIS"
	/usr/sbin/usermod -G amavis clamav 1>&2 > /dev/null
fi

%triggerin -- amavisd
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	echo "Adding clamav to amavis group GID=$AMAVIS"
	/usr/sbin/usermod -G amavis clamav 1>&2
fi

%pre
%groupadd -g 43 clamav
%useradd -u 43 -d /tmp -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav

# FIXME: check this. is it proper after useradd macro?
# TODO: use addusertogroup macro?
if [ -n "`/usr/bin/getgid amavis`" ]; then
	echo "Adding clamav to amavis group"
	/usr/sbin/usermod -G amavis clamav 1>&2
fi

%post
/sbin/chkconfig --add clamd
%service clamd restart "Clam Antivirus daemon"
touch /var/log/freshclam.log
chown clamav:root /var/log/freshclam.log
chmod 640 /var/log/freshclam.log

%preun
if [ "$1" = "0" ]; then
	%service clamd stop
	/sbin/chkconfig --del clamd
fi

%postun
if [ "$1" = "0" ]; then
	%userremove clamav
	%groupremove clamav
fi

%triggerpostun -- %{name} <= 0.75.1
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
%doc AUTHORS ChangeLog FAQ NEWS README docs/*.pdf
%attr(755,root,root) %{_bindir}/clamdscan
%attr(755,root,root) %{_bindir}/clamscan
%attr(755,root,root) %{_bindir}/freshclam
%attr(755,root,root) %{_bindir}/sigtool
%attr(755,root,root) %{_bindir}/clamconf
%attr(755,root,root) %{_sbindir}/clamd
%attr(755,root,root) %{_sbindir}/clamav-cron-updatedb
%attr(755,root,root) %{_sbindir}/clamav-post-updatedb
%attr(755,clamav,root) %dir /var/lib/%{name}
%ghost %attr(644,clamav,root) %verify(not md5 mtime size) /var/lib/clamav/*.cvd
%attr(640,clamav,root) %ghost /var/log/freshclam.log
%attr(750,clamav,clamav) %dir /var/run/%{name}

%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/clamd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/freshclam.conf

%attr(754,root,root) /etc/rc.d/init.d/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/clamav
%{_mandir}/man[15]/*
%{_mandir}/man8/clamd*

%if %{with milter}
%files milter
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/clamav-milter
%attr(754,root,root) /etc/rc.d/init.d/clamav-milter
#%attr(755,root,root) %{_sysconfdir}/cron.daily/clamav-milter
#%attr(755,root,root) %{_sysconfdir}/log.d/scripts/services/clamav-milter
#%{_sysconfdir}/log.d/conf/services/clamav-milter.conf
%attr(755,root,root) %{_sbindir}/clamav-milter
%{_mandir}/man8/clamav-milter.8*
%attr(700,clamav,clamav) /var/spool/clamav
%endif

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/clamav-config
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/*.h
%{_pkgconfigdir}/*.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a
