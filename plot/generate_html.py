#!/usr/bin/python3
import sys
import os
import ftplib
import shutil

# usage :
# generate_html <captionname> <repertoire_name on http://intra.cnrm.meteo.fr/algo/images/auger/>

#mycaption=[sys.argv[1],'reference','difference']
if '-h' in sys.argv:
    print('usage : generate_html <captionname> <repertoire_name on http://intra.cnrm.meteo.fr/algo/images/auger/>')
mycaption=['','','']

def generate_html(directory):
    # Get all PNG files from the directory
    a=os.listdir(directory)
    a.sort()
    png_files = [f for f in a if f.endswith('.png')]
    print(png_files)

    # Start the HTML structure
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Images Gallery</title>
        <style>
            .gallery {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                padding: 10px;
            }
            .gallery img {
                width: 100%;
                height: auto;
            }
            .caption {
                text-align: center;
                font-size: 40;
                padding: 5px;
            }
        </style>
    </head>
    <body>
        <div class="gallery">
    """

    # Add each image and its caption to the HTML content
    myindex=0
    for index, png in enumerate(png_files):
        html_content += f"""
        <div class="image-item">
            <img src="{directory}/{png}" alt="{png}">
#            <div class="caption">{mycaption[myindex%3]}</div>
            <div class="caption">{png}</div>
        </div>
        """
        myindex=myindex+1

    # Close the gallery and HTML tags
    html_content += """
        </div>
    </body>
    </html>
    """

    # Save the HTML content to a file
    html_filename = 'index.html'
    with open(html_filename, 'w') as f:
        f.write(html_content)

    print("HTML file 'index.html' generated successfully.")

    # Now, upload the HTML file and PNG files via FTP
    #upload_files_to_ftp(directory, png_files, html_filename)
    upload_files_to_copy(directory, png_files, html_filename)

def upload_files_to_copy(directory, png_files, html_filename):
        #remote_directory='/home/auger/.public/algo/auger/test'
        #try:
        # os.makedirs(remote_directory, exist_ok=True)
        #except:
        # pass
        #shutil.copy(directory+'/'+html_filename,remote_directory)
        #for png in png_files:
        #     shutil.copy(directory+'/'+png,remote_directory)
        myrep=sys.argv[2]
        print(myrep)
        os.system('ssh auger@sxalgo1.cnrm.meteo.fr \"mkdir -p /d0/images/auger/'+myrep+'\"')
        os.system('scp *png auger@sxalgo1.cnrm.meteo.fr:/d0/images/auger/'+myrep)
        os.system('scp index.html auger@sxalgo1.cnrm.meteo.fr:/d0/images/auger/'+myrep)

def upload_files_to_ftp(directory, png_files, html_filename):
    # FTP server credentials
    ftp_host = "ftp.yourserver.com"  # Replace with your FTP server
    ftp_user = "your_username"       # Replace with your FTP username
    ftp_password = "your_password"   # Replace with your FTP password
    remote_directory = "/path/to/remote/directory"  # Replace with the remote directory path
    try:
        # Connect to FTP server
        ftp = ftplib.FTP(ftp_host)
        ftp.login(ftp_user, ftp_password)

        # Create the remote directory if it does not exist
        try:
            ftp.mkd(remote_directory)
        except ftplib.error_perm:
            print(f"Directory {remote_directory} already exists.")

        # Change to the remote directory
        ftp.cwd(remote_directory)

        # Upload the HTML file
        with open(html_filename, 'rb') as f:
            ftp.storbinary(f"STORBINARY {html_filename}", f)
        print(f"Uploaded {html_filename} to FTP.")

        # Upload each PNG file
        for png in png_files:
            with open(os.path.join(directory, png), 'rb') as f:
                ftp.storbinary(f"STOR {png}", f)
            print(f"Uploaded {png} to FTP.")

        # Close the FTP connection
        ftp.quit()
        print("FTP upload complete.")

    except ftplib.all_errors as e:
        print(f"FTP error: {e}")


# Specify the directory where the PNG images are stored
directory = '.'  # Replace with your directory path
generate_html(directory)
print(f"images can be seen at http://intra.cnrm.meteo.fr/algo/images/auger/{directory}")

