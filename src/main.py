import os

def main():
    script_dir = os.path.dirname(__file__)
    rel_path = "../reqs/input-output/input-1"
    abs_path = os.path.join(script_dir, rel_path)
    with open(abs_path, "rb") as f:
        byte = f.read(1)
        while byte:
            byte = f.read(1)
            print(byte)

if __name__ == "__main__":
    main()
