Summary:	An anti-virus utility for Unix
Summary(pl):	Antywirusowe narzêdzie dla Unixów
Name:		clamav
Version:	0.50
Release:	1
License:	GPL
Group:		Applications
Source0:	http://clamav.elektrapro.com/stable/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		http://clamav.elektrapro.com/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Clam Antivirus is a powerful anti-virus scanner for Unix. It supports
AMaViS, compressed files, uses the virus database from
OpenAntivirus.org, and includes a program for auto-updating. The
scanner is multithreaded, written in C, and POSIX compliant.

%description -l pl
Clam Antivirus jest potê¿nym skanerem antywirusowym dla systemów
uniksowych. Wspiera on AMaViSa, skompresowane pliki, u¿ywa bazy
wirusów z OpenAntivirus.org, i posiada system automatycznej
aktualizacji. Skaner jest wielow±tkowy, napisany w C i zgodny z
POSIXem.

%package libs
Summary:        Shared libraries for clamav
Summary(pl):    Biblioteki dzielone clamav
Group:          Libraries

%description libs
Shared libraries for clamav.

%description libs -l pl
Biblioteki dzielone clamav.

%package devel
Summary:        clamav - Development header files and libraries
Summary(pl):    clamav - Pliki nag³ówkowe i biblioteki dla programistów
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}

%description devel
This package contains the development header files and libraries
necessary to develop clamav client applications.

%description devel -l pl
Pliki nag³ówkowe i biblioteki konieczne do kompilacji aplikacji
klienckich clamav.

%package static
Summary:        clamav staic libraris
Summary(pl):    Biblioteki statyczne clamav
Group:          Development/Libraries
Requires:       %{name}-devel = %{version}

%description static
clamav static libraris.

%description static -l pl
Biblioteki statyczne clamav.

%prep
%setup -q

%build
rm -f missing
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-clamav
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{rc.d/init.d,sysconfig}
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/cron.daily,%{_var}/log}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

echo -e '#!/bin/sh\n%{_bindir}/freshclam --quiet -l %{_var}/log/%{name}.log --daemon-notify' \
	> $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/%{name}

touch $RPM_BUILD_ROOT%{_var}/log/%{name}.log

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/clamd
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/clamd

%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ -n "`getgid clamav`" ]; then
        if [ "`getgid clamav`" != "43" ]; then
                echo "Warning: group clamav doesn't have gid=43. Correct this before installing clamav" 1>&2
                exit 1
        fi
else
	echo "adding group clamav GID=43"
        /usr/sbin/groupadd -g 43 -r -f clamav
fi
if [ -n "`id -u clamav 2>/dev/null`" ]; then
	if [ "`id -u clamav`" != "43" ]; then
		echo "Warning: user clamav doesn't have uid=43. Correct this before installing clamav" 1>&2
		exit 1
	fi
else
	echo "Adding user clamav UID=43"
	/usr/sbin/useradd -u 43 -r -d /tmp  -s /bin/false -c "Clam Anti Virus Checker" -g clamav clamav 1>&2
fi

%postun
if [ "$1" = "0" ]; then
	echo "Removing user clamav"
	/usr/sbin/userdel clamav
	echo "Removing group clamav"
	/usr/sbin/groupdel clamav
fi

%post
touch %{_var}/log/%{name}.log && chmod 640 %{_var}/log/%{name}.log && chown clamav %{_var}/log/%{name}.log

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog FAQ NEWS README TODO docs/html/
%attr(755,root,root) %{_bindir}/*
%attr(755,clamav,root) %dir %{_datadir}/%{name}
%attr(644,clamav,root) %verify(not md5 size mtime) %{_datadir}/%{name}/*.db*
%attr(640,clamav,root) %ghost %{_var}/log/%{name}.log
%attr(750,root,root) %{_sysconfdir}/cron.daily/%{name}
%attr(644,root,root) %config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/*.conf
%attr(754,root,root) %{_sysconfdir}/rc.d/init.d/clamd
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/clamd
%{_mandir}/man?/*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%attr(755,root,root) %{_libdir}/lib*.la
%{_includedir}/*.h

%files static
%defattr(644,root,root,755)
%{_libdir}/*.a
