Summary:	Antivirus for Unix
Summary(pl):	Antywirus dla Unixów
Name:		clamav
Version:	0.11
Release:	1
License:	GPL
Group:		System/Tools
######		/home/mick3y/rpm/SOURCES/rpm.groups: no such file
Source0:	http://www.konarski.edu.pl/~zolw/clam/%{name}-%{version}.tar.gz
URL:		http://www.konarski.edu.pl/~zolw/clam.html
BuildRequires:	autoconf
BuildRequires:	automake
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

#%define		datadir		/var/lib

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

%prep
%setup -q

%build
%configure2_13 \
	--disable-clamav \
	--with-datadir=%{_datadir}/clam
%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_prefix},%{_bindir},%{_mandir},%{_datadir}/clam}

%{__make} prefix=$RPM_BUILD_ROOT%{_prefix} bindir=$RPM_BUILD_ROOT%{_bindir} mandir=$RPM_BUILD_ROOT%{_mandir} datadir=$RPM_BUILD_ROOT%{_datadir}/clam install
gzip -9nf AUTHORS FAQ TODO

%clean
rm -fr $RPM_BUILD_ROOT

%pre
if [ -z "`id -u clanav 2>/dev/null`" ]; then
 /usr/sbin/useradd -u 95 -r -d /usr/share/clam -s /bin/false -c "ClamAV" -g nobody clamav 1>&2
fi

%post
 /usr/sbin/userdel clamav
fi

%files
%defattr(644,root,root,755)
%{_datadir}
%attr(751,root,root)%{_bindir}/
#{clamscan,freshclam}
%doc *.gz
