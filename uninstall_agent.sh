#!/bin/bash

agOwn=$1
install_path="/opt/controlm/${agOwn}"
config_dat="/opt/controlm/${agOwn}/ctm/data/CONFIG.dat"
agPackage="control-m-AGENT${agOwn: -1}"

dateTime=$(date +'%Y%m%d%H%M%S')
log_file="/tmp/dba_uninstall_agent_${dateTime}.txt"

backup_config_file() {
  status_code=0
  cp "$config_dat" "$install_path/uninstall_bak_CONFIG.dat.$dateTime" >> "$log_file" 2>&1
  if [ $? -ne 0 ]; then
    status_code=1
    status_msg="Failed to backup CONFIG.dat file"
  else
    status_msg="Successfully backed up CONFIG.dat file"
  fi

  echo "$status_msg" >> "$log_file"
  return $status_code
}

uninstall_package() {
  status_code=0
  yum remove -y "$agPackage" >> "$log_file" 2>&1
  if [ $? -ne 0 ]; then
    status_code=1
    status_msg="Failed to uninstall package $agPackage"
  else
    status_msg="Successfully uninstalled package $agPackage"
  fi

  echo "$status_msg" >> "$log_file"
  return $status_code
}

clean_processes() {
  status_code=0
  processes=$(ps -ef | grep "${agOwn}" | grep -v grep | awk '{print $2}')
  if [ -n "$processes" ]; then
    kill -9 $processes >> "$log_file" 2>&1
    sleep 3

    processes_remaining=$(ps -ef | grep "${agOwn}" | grep -v grep | wc -l)

    if [[ $processes_remaining -gt 0 ]]; then
      status_msg="Warning: Still identified $processes_remaining hang up processes after killing, please verify manually with command 'ps -ef | grep "${agOwn}" | grep -v grep', contact support team if needed."
    else
      status_msg="Successfully killed all processes containing $agOwn"
    fi
  else
    status_msg="Successfully killed all processes containing $agOwn"
  fi

  echo "$status_msg" >> "$log_file"
  return $status_code
}

cleanup_files() {
  status_code=0
  files=($(ls "$install_path"/*))

  for file in "${files[@]}"; do
    if [ "$file" != "$install_path/uninstall_bak_CONFIG.dat.$dateTime" ]; then
      rm -rf "$file" >> "$log_file" 2>&1
    fi

    if [ $? -ne 0 ]; then
      status_code=1
      status_msg="Failed to cleanup files under $file"
    else
      status_msg="Successfully cleaned up file/folder $file"
    fi

    echo "$status_msg" >> "$log_file"
  done

  return $status_code
}

verify_cleanup() {
  files_remaining=$(ls -1A "$install_path" | grep -v '^uninstall_bak_CONFIG.dat\.' | wc -l)
  if [[ $files_remaining -gt 1 ]]; then
    echo "Verify home directory after uninstalled: " >> "$log_file"
    ls -l "$install_path" | grep -v '^uninstall_bak_CONFIG.dat\.' >> "$log_file"
    status_msg="Warning: $((files_remaining - 1)) files remaining in $install_path. Please check and cleanup manually."
  else
    remaining_file=$(ls -1A "$install_path")
    if [[ $remaining_file == uninstall_bak_CONFIG.dat.* ]]; then
      status_msg="Cleanup verification passed, only backup file remains"
    else
      status_msg="Warning: Unexpected folder/files [ $((files_remaining - 1)) ] remains in $install_path. Please check and cleanup manually."
    fi
  fi

  echo "$status_msg" >> "$log_file"
}

backup_config_file
backup_config_file_status_code=$?

uninstall_package
uninstall_package_status_code=$?

clean_processes
clean_processes_status_code=$?

cleanup_files
cleanup_files_status_code=$?

verify_cleanup

last_line=$(tail -1 "$log_file")
echo "Final status: $last_line"
exit ${cleanup_files_status_code}
