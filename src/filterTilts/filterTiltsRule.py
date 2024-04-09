# automatically exclude tilts based on parameters determined in motioncorr and ctffind (before ML)
import os
import sys
import pandas as pd

from src.rw.librw import read_star, write_star
from src.filterTilts.libFilterTilts import col_of_df_to_series, series_higher_lower,combine_vectors,remove_tilts


def filterTiltsRule(tsStar,out_dir,shift_init=None,defocus_init=None,res_init=None):
    """  
    loop through the tilt series found in the .star file and perform the respective functions on them
    to exclude tilts that are not within the set range of the respective parameter. 


    Example:
        path_tilt_series_ctf_star = /fs/pool/pool-plitzko3/Michael/01-Data/relion/pipeline_test/schemes/CtfFind/job122/tilt_series_ctf.star
        param_range_dict = {"rlnCtfMaxResolution": (8, 9)}
    """
    param_range_dict = ({})

    # Turn the str of the input into tuples and add to dict if they are given
    if shift_init:
        shift = tuple(map(float, shift_init.split("-")))
        param_range_dict["rlnAccumMotionTotal"] = shift

    if defocus_init:
        defocus = tuple(map(float, defocus_init.split("-")))
        param_range_dict["rlnDefocusU"] = defocus

    if res_init:
        res = tuple(map(float, res_init.split("-")))
        param_range_dict["rlnCtfMaxResolution"] = res


    # Make dir for individual tilt series' .star files
    tilt_series_dir = os.path.join(out_dir, "tilt_series")
    os.makedirs(tilt_series_dir, exist_ok=True)

    # Get working dir and input directory to construct the absolute path to the .star file
    abs_path_to_ctf_star = os.path.join(os.getcwd(), tsStar)
    tilt_series_ctf_star_df = read_star(abs_path_to_ctf_star)

    for index, current_tilt in tilt_series_ctf_star_df.iterrows():
        indiv_tilt_star_path = current_tilt["rlnTomoTiltSeriesStarFile"]
        tilt_star_dict = read_star(indiv_tilt_star_path, do_dict = True)
        tilt_star_dict_name_of_df = current_tilt["rlnTomoName"]
        tilt_star_df = tilt_star_dict[tilt_star_dict_name_of_df]

        all_0_1_across_params = pd.DataFrame(index = range(len(tilt_star_df)), columns = (param_range_dict.keys()))

        for param, thresholds in param_range_dict.items():
            current_param = col_of_df_to_series(tilt_star_df, param)
            param_runaways = series_higher_lower(current_param, thresholds)
            all_0_1_across_params[param] = param_runaways
        
        tilts_to_keep = combine_vectors(all_0_1_across_params)
        updated_df = remove_tilts(tilt_star_df, tilts_to_keep)
        updated_star_as_dict = {tilt_star_dict_name_of_df: updated_df}
        # Individual tilts are called CtfFind/jobXXX/tilt_series/Position_YY.star --> only want last part as file name
        file_name = indiv_tilt_star_path.split("/")[-1]
        new_path = os.path.join(tilt_series_dir, file_name)
        write_star(updated_star_as_dict, new_path)

    # Write a star file pointing to the updated tilt_series/Position_YY.star files as input for next job
    # Get the current job number
    tilt_series_star_list = col_of_df_to_series(tilt_series_ctf_star_df, "rlnTomoTiltSeriesStarFile")
    tilt_series_ctf_star_dict = read_star(abs_path_to_ctf_star, do_dict = True)
    
    name_jobXXX = out_dir.split("/")[1]
    name_job_number = name_jobXXX.split("job")[1]

    # Change the name of the files being pointed to (CtfFind/jobXXX/tilt_series/Position_10.star to External/jobYYY/tilt_series/Position_10.star)
    part_to_replace = tilt_series_star_list[0].split("/tilt_series")[0]
    updated_tilt_series_star_col = tilt_series_star_list.str.replace(part_to_replace, f"External/job{name_job_number}")
    # Replace the column pointing to the old .star files with the new series
    tilt_series_ctf_star_dict["global"]["rlnTomoTiltSeriesStarFile"] = updated_tilt_series_star_col
    # Write the star file
    updated_tilt_series_star_path = os.path.join(os.getcwd(), out_dir, "excluded_tilts_rule.star")
    
    write_star(tilt_series_ctf_star_dict, updated_tilt_series_star_path)



