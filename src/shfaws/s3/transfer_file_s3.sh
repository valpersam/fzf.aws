#######################################
# handle operation between buckets
# Globals:
#   None
# Arguments:
#   $1: operation cmd cp/mv/sync
#   $2: from bucket path
#   $3: to bucket path
#   $4: recursive flag
# Outputs:
#   None
#######################################
function transfer_file_s3() {
  local operation_cmd="$1"
  local from_path="$2"
  local to_path="$3"
  local recursive="$4"

  # display dryrun information and ask for confirmation
  # sync doesn't accpet recursive flag, it perform recursive by default
  if [[ -z "${recursive}" || "${operation_cmd}" == 'sync' ]]; then
    aws s3 "${operation_cmd}" "s3://${from_path}" "s3://${to_path}" --dryrun
  else
    aws s3 "${operation_cmd}" "s3://${from_path}" "s3://${to_path}" --recursive --dryrun
  fi
  get_confirmation "Confirm?"

  # perform operation
  if [[ "${confirm}" == 'y' ]]; then
    if [[ -z "$recursive" || "${operation_cmd}" == 'sync' ]]; then
      aws s3 "${operation_cmd}" "s3://${from_path}" "s3://${to_path}"
    else
      aws s3 "${operation_cmd}" "s3://${from_path}" "s3://${to_path}" --recursive
    fi
  fi
  exit 0
}