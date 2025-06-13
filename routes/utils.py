# routes/utils.py
import re
from bs4 import BeautifulSoup
import os

def clean_llm_markdown_output(output_str: str) -> str:
    if not output_str: return ""
    cleaned_str = re.sub(r"^```(?:markdown)?\s*|\s*```$", "", output_str.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return cleaned_str.strip()

def get_plain_text_from_html(html_content: str) -> str:
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator='\n', strip=True)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text


def cleanup_temp_files(directory: str, max_files_to_keep_per_prefix: int = 5) -> str:
    """
    Cleans up temporary files in the specified directory, keeping only the
    most recent N files for each defined prefix.
    Returns a log string summarizing the cleanup.
    """
    log_messages = [f"INFO: [Cleanup] Starting cleanup for directory: {directory}"]
    # print(f"DEBUG: [Cleanup] Target directory: {directory}") # Print directory

    prefixes_extensions = {
        "jd_": ".txt",
        "opr_": ".json",
        "pdf_": ".json", # This is for the temp file holding data for PDF generation
        "feedback_": ".txt"
    }
    
    total_deleted_count = 0

    for prefix, extension in prefixes_extensions.items():
        
        files_with_mtime = []
        try:
            all_files_in_dir = os.listdir(directory)

            for f_name in all_files_in_dir:
                # print(f"DEBUG: [Cleanup] Checking file: {f_name}") # Can be very verbose
                if f_name.startswith(prefix) and f_name.endswith(extension):
                    full_path = os.path.join(directory, f_name)
                    try:
                        mtime = os.path.getmtime(full_path)
                        files_with_mtime.append((full_path, mtime))
                    except FileNotFoundError:
                        # print(f"WARN: [Cleanup] FileNotFoundError for {full_path} during getmtime (possibly deleted concurrently). Skipping.")
                        continue
                    except Exception as e_mtime:
                        # print(f"ERROR: [Cleanup] Error getting mtime for {full_path}: {e_mtime}")
                        continue
        except Exception as e_list:
            # err_msg_list = f"ERROR: [Cleanup] Could not list or process files for prefix '{prefix}': {e_list}"
            # log_messages.append(err_msg_list)
            # print(err_msg_list) # Print to console
            continue # Skip to next prefix


        if len(files_with_mtime) > max_files_to_keep_per_prefix:
            files_with_mtime.sort(key=lambda x: x[1]) # Sort by mtime (oldest first)
            
            files_to_delete_count = len(files_with_mtime) - max_files_to_keep_per_prefix
            files_to_delete_paths = [f_tuple[0] for f_tuple in files_with_mtime[:files_to_delete_count]]
            
            # msg = f"INFO: [Cleanup] Prefix '{prefix}': Found {len(files_with_mtime)} files, keeping {max_files_to_keep_per_prefix}, attempting to delete {files_to_delete_count}."
            # log_messages.append(msg)
            # print(msg) 
            
            deleted_this_prefix = 0
            for f_path in files_to_delete_paths:
                # print(f"DEBUG: [Cleanup] Attempting to delete: {f_path}")
                try:
                    os.remove(f_path)
                    # print(f"INFO: [Cleanup] Successfully deleted: {f_path}")
                    deleted_this_prefix += 1
                except Exception as e_remove:
                    err_msg_remove = f"ERROR: [Cleanup] Could not delete temp file {f_path}: {e_remove}"
                    log_messages.append(err_msg_remove)
                    # print(err_msg_remove) # Print to console
            
            if deleted_this_prefix > 0:
                log_messages.append(f"INFO: [Cleanup] Successfully deleted {deleted_this_prefix} files for prefix '{prefix}'.")
            total_deleted_count += deleted_this_prefix
        else:
            msg = f"INFO: [Cleanup] Prefix '{prefix}': Found {len(files_with_mtime)} files, which is within limit of {max_files_to_keep_per_prefix}. No deletion needed for this prefix."
            log_messages.append(msg)
            # print(msg) # Print to console
    
    if total_deleted_count > 0:
        log_messages.append(f"INFO: [Cleanup] Total old files deleted across all prefixes: {total_deleted_count}")
    else:
        log_messages.append("INFO: [Cleanup] No old files were deleted across all prefixes based on current limits.")
    
    log_messages.append("INFO: [Cleanup] Cleanup process finished.")
    # print("INFO: [Cleanup] Cleanup process finished. Returning log string.")
    return "\n".join(log_messages)