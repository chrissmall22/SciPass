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
          'openvswitch-switch'
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



