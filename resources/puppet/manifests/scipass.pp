$deps = [ 'build-essential',
          'debhelper',
          'dkms',
          'fakeroot',
          'graphviz',
          'linux-headers-generic',
          'python-all',
          'python-qt4',
          'python-zopeinterface',
          'python-twisted-conch',
          'python-twisted-web',
          'xauth',
          'openvswitch-switch',
          'python-coverage',
          'python-mock',
          'python-ipaddr',
          'python-libxml2',
          'python-lxml',
          'python-webob',
          'python-routes',
          'python-paramiko',
          'python-oslo.config',
          'python-netaddr',
          'msgpack-python',
          'python-greenlet',
          'python-pip',
          'python-dev'
]

package { $deps:
    ensure   => installed,
}

vcsrepo { '/home/vagrant/mininet':
    ensure   => present,
    provider => git,
    user     => 'vagrant',
    source   => 'git://github.com/mininet/mininet',
    revision => '2.1.0p2',
    before   => Exec['Install Mininet']
}

exec { 'Install Mininet':
    command => 'bash mininet/util/install.sh -nf > /dev/null',
    cwd     => '/home/vagrant',
    user    => 'vagrant',
    path    => $::path,
    timeout => 0
}

exec {'ODL-2.0':
    command => 'wget http://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.2.0-Helium/distribution-karaf-0.2.0-Helium.tar.gz',
    cwd     => '/home/vagrant',
    path    => $::path,
    user    => 'vagrant'
}

exec { 'Extract ODL':
    command => 'tar -xvf distribution-karaf-0.2.0-Helium.tar.gz',
    cwd     => '/home/vagrant',
    user    => 'vagrant',
    path    => $::path,
    timeout => 0,
    require => Exec['ODL-2.0']
}

vcsrepo { '/home/vagrant/scinet':
    ensure   => present,
    provider => git,
    user     => 'vagrant',
    source   => 'git://github.com/chrissmall22/SciPass',
    revision => 'odl'
}

vcsrepo { '/home/vagrant/ryu':
    ensure   => present,
    provider => git,
    user     => 'vagrant',
    source   => 'https://github.com/osrg/ryu',
    before   => Exec['Install Ryu']
}

exec { 'Install Ryu':
    command => 'python ./setup.py install',
    cwd     => '/home/vagrant/ryu',
    user    => 'vagrant',
    path    => $::path,
    timeout => 0
}