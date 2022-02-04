node default {
  file { '/root/README':
    ensure => file,
    content => 'This is a readme\t',
    owner   => 'root',
  }
  file { '/root/README':
    owner => 'root',
    }
}
