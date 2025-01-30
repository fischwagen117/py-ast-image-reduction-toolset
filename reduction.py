def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="Image file path to reduction.")
    parser.add_argument("mbias_path", help="Master bias file path.")
    parser.add_argument("mdark_path", help="Master dark file path.")
    parser.add_argument("mflat_path", help="Master flat file path.")
    args = parser.parse_args()
    return args
    
def main(args):
    from proc import create_reduced_image
    from glob import glob
    from configparser import ConfigParser

    config = ConfigParser()
    config.read("./config.cfg")
    bin_size = int(config["REDUCTION_PARAMS"]["bin_size"])
    flat_corr_min_val = float(config["REDUCTION_PARAMS"]["flat_corr_min_val"])
    exp_key = config["HEADER_KEYS"]["EXPOSURE_KEY"]
    hot_pix_file = config["PATHS"]["hot_pix_flie_path"]

    image_path = args.image_path
    mbias_path = args.mbias_path
    mdark_path = args.mdark_path
    mflat_path = args.mflat_path

    images = glob(image_path)
    for image in images:
        image_name_comps = image.split(".")
        output_name = f"{image_name_comps[0]}_out.{image_name_comps[1]}"
        create_reduced_image(image, mbias_path, mdark_path, mflat_path, output_name, hot_pix_file, exp_key, bin_size, flat_corr_min_val)

if __name__ == "__main__":
    import argparse
    args = parse_args()
    main(args)
