node default {
  file { '/root/README':
    ensure => file,
    content => 'This is a readme',
    owner   => 'root',
  }
}
node 'puppet-ag1' {
  include role::master_server
}
node /^web/ { 
  include role::app_server
}
node /^db/ {
  include role::db_server
}
