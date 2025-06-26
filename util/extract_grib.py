#!/opt/softs/anaconda3/bin/python3
import sys


def copy_binary_file(source_file, destination_file,nwrite_record):
    nrecord=0
    nlengthread=0
    lwrite = False
    last_four_bytes = bytearray()
    try:
        with open(source_file, 'rb') as src, open(destination_file, 'wb') as dst:
            while True:
                byte = src.read(1)
           #     nlengthread+=1
           #     print(byte)
           #     if nlengthread==20:
           #        sys.exit()
                if not byte:
                    break
                if len(last_four_bytes) >= 4:
                    last_four_bytes = last_four_bytes[-3:] + byte
                else:
                    last_four_bytes += byte 
                if len(last_four_bytes) >= 4:
                    if last_four_bytes == b'GRIB':
                      nrecord+=1
                      print(nrecord)
                      if nrecord == nwrite_record:
                         lwrite = True
                    if lwrite == True:
                         dst.write(last_four_bytes[0].to_bytes(1,'big')) 
                    if last_four_bytes == b'7777':
                         print("end grib message")
                    if last_four_bytes == b'7777' and lwrite == True:
                         lwrite = False
#                         dst.write(last_four_bytes[0].to_bytes(1,'big'))
                         dst.write(last_four_bytes[1].to_bytes(1,'big'))
                         dst.write(last_four_bytes[2].to_bytes(1,'big'))
                         dst.write(last_four_bytes[3].to_bytes(1,'big'))
                         sys.exit()
        print(f"Le fichier {source_file} a été copié avec succès vers {destination_file}.")
    except FileNotFoundError:
        print(f"Le fichier {source_file} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# Exemple d'utilisation

source_file = sys.argv[1]
destination_file = sys.argv[2]
copy_binary_file(source_file, destination_file,int(sys.argv[3]))
