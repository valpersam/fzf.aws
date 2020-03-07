#######################################
# upload file to s3
# Globals:
#   None
# Arguments:
#   $1: operation_cmd cp/mv/rm
#   $2: s3 path to upload
#   $3: recursive flag
#   $4: hidden flag
#   $5: search from root flag
#   $6: local path
# Outputs:
#   None
#######################################
function upload_file_s3() {
  local operation_cmd=$1
  local s3_path=$2
  local recursive=$3
  local hidden=$4
  local search_from_root=$5
  local local_path=$6

  [[ -n "${search_from_root}" ]] && cd "${HOME}"
  # get local file path
  if [[ -z "${local_path}" ]]; then
    if [[ -z "${recursive}" ]]
    then
      echo "select a file to upload"
      local_path=$(search_file 'file' "${hidden}")
    else
      echo "select a folder to upload"
      local_path=$(search_file 'folder' "${hidden}")
    fi
  fi
  if [[ -z "${local_path}" ]]; then
    if [[ "$operation_cmd" == 'sync' ]]; then
      local_path="${PWD}/"
      echo "${local_path} will be synced with the selected bucket"
    else
      echo "No local path selected"
      exit 1
    fi
  fi

  # display dryrun info and get confirmation
  # sync doesn't accpet recursive flag, it perform recursive by default
  if [[ -z "${recursive}" || "${operation_cmd}" == 'sync' ]]; then
    aws s3 "${operation_cmd}" "${local_path}" "s3://${s3_path}" --dryrun
  else
    aws s3 "${operation_cmd}" "${local_path}" "s3://${s3_path}" --dryrun --recursive
  fi
  get_confirmation "Confirm?"
  # upload to s3
  if [[ "${confirm}" == 'y' ]]; then
    if [[ -z "${recursive}" || "${operation_cmd}" == 'sync' ]]; then
      aws s3 "${operation_cmd}" "${local_path}" "s3://${s3_path}"
    else
      aws s3 "${operation_cmd}" "${local_path}" "s3://${s3_path}" --recursive
    fi
  fi
  exit 0
}
