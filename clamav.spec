# TODO:
#   Make freshclam (script and daemon)

Summary:	An anti-virus utility for Unix
Summary(pl):	Antywirusowe narz�dzie dla Uniks�w
Name:		clamav
Version:	0.75.1
Release:	2
License:	GPL
Group:		Applications
Source0:	http://dl.sourceforge.net/clamav/%{name}-%{version}.tar.gz
# Source0-md5:	2c85b7957eba9fd9e9ff8c2537ae006f
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source4:	%{name}-cron-updatedb
Source5:	%{name}.logrotate
# Remember to update date after databases upgrade
%define		database_version	20040731
Source6:	http://www.clamav.net/database/daily.cvd
# Source6-md5:	8aa799fff39b3dd7c36a7dd796890b66
Source7:	http://www.clamav.net/database/main.cvd
# Source7-md5:	fb569320447dff5b22acdbec2dbc5772
Source8:	%{name}-post-updatedb
Patch0:		%{name}-pld_config.patch
Patch1:		%{name}-no_auto_libwrap.patch
URL:		http://www.clamav.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gmp-devel
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name}-libs = %{version}-%{release}
Requires:	bc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Clam Antivirus is a powerful anti-virus scanner for Unix. It supports
AMaViS, compressed files, on-access scanning and includes a program
for auto-updating with support for digital signatures.
The virus database has over 20000 viruses, worms and trojans signatures.
The scanner is multithreaded, written in C, and POSIX compliant.

%description -l pl
Clam Antivirus jest pot�nym skanerem antywirusowym dla system�w
uniksowych. Wspiera on AMaViSa, skompresowane pliki, skanowanie "on-access"
i posiada system bezpiecznej, automatycznej aktualizacji.
Baza wirus�w zawiera ponad 20000 sygnatur. Skaner jest wielow�tkowy,
napisany w C i zgodny z POSIXem.

%package libs
Summary:	Shared libraries for clamav
Summary(pl):	Biblioteki dzielone clamav
Group:		Libraries

%description libs
Shared libraries for clamav.

%description libs -l pl
Biblioteki dzielone clamav.

%package devel
Summary:	clamav - Development header files and libraries
Summary(pl):	clamav - Pliki nag��wkowe i biblioteki dla programist�w
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the development header files and libraries
necessary to develop clamav client applications.

%description devel -l pl
Pliki nag��wkowe i biblioteki konieczne do kompilacji aplikacji
klienckich clamav.

%package static
Summary:	clamav static libraris
Summary(pl):	Biblioteki statyczne clamav
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
clamav static libraries.

%description static -l pl
Biblioteki statyczne clamav.

%package database
Summary:	Virus database for clamav
Summary(pl):	Bazy wirus�w dla clamav
Group:		Applications
Version:	%{version}.%{database_version}
PreReq:		%{name}

%description database
Virus database for clamav (updated %{database_version}).

%description database -l pl
Bazy wirus�w dla clamav (aktualizowana %{database_version}).

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-clamav \
	--with-dbdir=/var/lib/%{name}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{rc.d/init.d,sysconfig,logrotate.d} \
	$RPM_BUILD_ROOT{%{_sysconfdir}/cron.d,%{_var}/log}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

cat <<EOF >$RPM_BUILD_ROOT%{_sysconfdir}/cron.d/%{name}
5 * * * *	root	%{_sbindir}/clamav-cron-updatedb
EOF


install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/clamd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/clamd
install %{SOURCE4} $RPM_BUILD_ROOT%{_sbindir}/clamav-cron-updatedb
install etc/*.conf $RPM_BUILD_ROOT%{_sysconfdir}/
install %{SOURCE5} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}
install %{SOURCE6} $RPM_BUILD_ROOT/var/lib/%{name}/
install %{SOURCE7} $RPM_BUILD_ROOT/var/lib/%{name}/
install %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}

# NOTE: clamd uses sane rights to it's clamd.pid file
# So better keep it dir
# If it is fixed use of dir will be unecesary
install -d $RPM_BUILD_ROOT%{_var}/run/%{name}

touch $RPM_BUILD_ROOT%{_var}/log/freshclam.log

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- amavis-ng
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	/usr/sbin/usermod -G amavis clamav 1>&2 > /dev/null
	echo "adding clamav to amavis group GID=$AMAVIS"
fi

%triggerin -- amavisd-new
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	/usr/sbin/usermod -G amavis clamav 1>&2 > /dev/null
	echo "adding clamav to amavis group GID=$AMAVIS"
fi

%triggerin -- amavisd
AMAVIS=$(/usr/bin/getgid amavis)
RESULT=$?
if [ $RESULT -eq 0 ]; then
	/usr/sbin/usermod -G amavis clamav 1>&2 > /dev/null
	echo "adding clamav to amavis group GID=$AMAVIS"
fi


%pre
if [ -n "`getgid clamav`" ]; then
	if [ "`getgid clamav`" != "43" ]; then
		echo "Warning: group clamav doesn't have gid=43. Correct this before installing clamav" 1>&2
		exit 1
	fi
else
	echo "Adding group clamav GID=43"
	/usr/sbin/groupadd -g 43 -r -f clamav
fi
if [ -n "`id -u clamav 2>/dev/null`" ]; then
	if [ "`id -u clamav`" != "43" ]; then
		echo "Warning: user clamav doesn't have uid=43. Correct this before installing clamav" 1>&2
		exit 1
	fi
else
	echo "Adding user clamav UID=43"
	/usr/sbin/useradd -u 43 -r -d /tmp -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav 1>&2
fi

%post
/sbin/chkconfig --add clamd
if [ -f /var/lock/subsys/clamd ]; then
	/etc/rc.d/init.d/clamd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/clamd start\" to start Clam Antivirus daemon." >&2
fi
touch %{_var}/log/freshclam.log
chown clamav:root %{_var}/log/freshclam.log
chmod 640 %{_var}/log/freshclam.log

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/clamd ]; then
		/etc/rc.d/init.d/clamd stop
	fi
	/sbin/chkconfig --del clamd
fi

%postun
if [ "$1" = "0" ]; then
	echo "Removing user clamav"
	/usr/sbin/userdel clamav
	echo "Removing group clamav"
	/usr/sbin/groupdel clamav
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%post	database -p %{_sbindir}/%{name}-post-updatedb

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS README TODO docs/html/
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_sbindir}/*
%attr(755,clamav,root) %dir /var/lib/%{name}
%attr(640,clamav,root) %ghost %{_var}/log/freshclam.log
%attr(750,clamav,clamav) %dir %{_var}/run/%{name}

%attr(640,root,root) %{_sysconfdir}/cron.d/%{name}
%attr(644,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/clamav.conf
%attr(644,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/freshclam.conf

%attr(754,root,root) /etc/rc.d/init.d/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/sysconfig/clamd
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/clamav
%{_mandir}/man?/*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/*.h
%{_pkgconfigdir}/*.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a

%files database
%defattr(644,root,root,755)
%attr(644,clamav,root) %verify(not md5 size mtime) /var/lib/%{name}/*.cvd