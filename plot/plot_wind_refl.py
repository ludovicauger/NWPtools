#!/usr/bin/env python3
import os
import ftplib
import netrc
import datetime as dt

import numpy as np
import matplotlib
matplotlib.use('Agg')          # pas d'affichage interactif : on ne fait que des .png
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import epygram

epygram.init_env()


# ----------------------------------------------------------------------------
# Recuperation d'un fichier sur hendrix par FTP
# ----------------------------------------------------------------------------
HENDRIX = 'hendrix.meteo.fr'


def get_hendrix_credentials(host=HENDRIX):
    """Login/mot de passe pour hendrix.

    Cherche dans ~/.netrc, puis dans les variables d'environnement
    HENDRIX_USER / HENDRIX_PASSWD.
    """
    try:
        auth = netrc.netrc().authenticators(host)
        if auth is not None:
            login, _, passwd = auth
            return login, passwd
    except (IOError, netrc.NetrcParseError):
        pass

    login = os.environ.get('HENDRIX_USER')
    passwd = os.environ.get('HENDRIX_PASSWD')
    if login and passwd:
        return login, passwd

    raise RuntimeError(
        f"Pas d'identifiants pour {host} : cree un ~/.netrc "
        f"(machine {host} login xxx password yyy, chmod 600) "
        f"ou exporte HENDRIX_USER et HENDRIX_PASSWD")


def ftp_get(remote_path, local_path, host=HENDRIX, login=None, passwd=None,
            overwrite=False):
    """Rapatrie remote_path depuis le serveur FTP host vers local_path.

    Renvoie True si le fichier est disponible en local, False sinon.
    """
    if os.path.exists(local_path) and not overwrite:
        print(f'  deja present en local : {local_path}')
        return True

    if login is None or passwd is None:
        login, passwd = get_hendrix_credentials(host)

    tmp_path = local_path + '.part'
    print(f'  ftp get {host}:{remote_path} -> {local_path}')
    try:
        with ftplib.FTP(host, timeout=300) as ftp:
            ftp.login(login, passwd)
            ftp.set_pasv(True)
            with open(tmp_path, 'wb') as fh:
                ftp.retrbinary('RETR ' + remote_path, fh.write)
    except ftplib.all_errors + (OSError,) as err:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f'  ECHEC ftp : {err}')
        return False

    os.replace(tmp_path, local_path)
    return True


# ----------------------------------------------------------------------------
# Parametres
# ----------------------------------------------------------------------------
xmin, xmax = 1.2, 3.
ymin, ymax = 42.8, 44.
# domaine plus large
# xmin, xmax = 1.1, 3.5
# ymin, ymax = 42.1, 44.
# zoom
# xmin, xmax = 1.8, 2.6
# ymin, ymax = 42.9, 43.4
# super zoom
# xmin, xmax = 2.15, 2.45
# ymin, ymax = 43.1, 43.25

extent_tot = [xmin, xmax, ymin, ymax]

# point d'interet
lon_point = 2.3
lat_point = 43.115

YYMM = '202608'
SUBSAMPLING = 5

# format de sortie : 'pdf' (vectoriel, zoom illimite sur les fleches et les
# contours) ou 'png' (tramé)
FMT = 'pdf'

# resolution : ne concerne que les elements trames (le champ de reflectivite),
# en png comme dans un pdf. DPI x taille de figure (en pouces) = pixels
DPI = 200

# allure des fleches de vent, en multiples de la largeur du fut
# (defauts matplotlib : headwidth=3, headlength=5, headaxislength=4.5)
# scale for the vector length , higher means shorter, width vector width
#QUIVER_KW = dict(scale=12000, headwidth=2., headlength=2.5, headaxislength=2., width=0.001)
QUIVER_KW = dict(scale=5000, headwidth=3., headlength=5, headaxislength=4.5, width=0.001)

# repertoire de travail pour les grib rapatries et les images
workdir = os.getcwd()

# racine des donnees sur hendrix
hendrix_root = '/home/auger/vortex/arome/custom'

for exp in ['HCQ1','HCQ4']:
    for jj in ['24']:
        for res in ['00']:
            for ech in ['011','012','013','014','015','016','017','018','019']:
            #for ech in ['011']:
                # liste_mn = ['00','05','10','15','20','25','30','35','40','45','50','55']
                liste_mn = ['00','15','30','45']
                #liste_mn = ['00']
                #if ech == '015':
                #    liste_mn = ['00']

                for mn in liste_mn:
                    print(jj, res, ech, mn)

                    date_courante = f'{YYMM}{jj}T{res}00P_{ech}_{mn}'

                    remote = (f'{hendrix_root}/{exp}/{YYMM}{jj}T{res}00P/forecast/'
                              f'grid.arome-forecast.custom-00km00+0{ech}:{mn}.grib')
                    local = os.path.join(
                        workdir, f'grid_{exp}_{date_courante}.grib')

                    if not ftp_get(remote, local):
                        print('  -> echeance sautee')
                        continue

                    fcst = epygram.formats.resource(local, 'r')
                    try:
                        # reflectivite
                        var = fcst.readfield('parameterCategory: 16, '
                                             'parameterNumber: 4, '
                                             'typeOfFirstFixedSurface: 1')
                        vraf = var.extract_zoom(dict(lonmin=xmin, lonmax=xmax,
                                                     latmin=ymin, latmax=ymax))
                        fig, ax = vraf.cartoplot(colormap='reflsyn',
                                                 epygram_departments=True)

                        # vent 10 m
                        u = fcst.readfield('shortName: 10u')
                        v = fcst.readfield('shortName: 10v')
                        # rafales : 10efg / 10nfg
                        # u = fcst.readfield('shortName: 10efg')
                        # v = fcst.readfield('shortName: 10nfg')
                        # u.operation('*', 1.94384)   # m/s => kt
                        # v.operation('*', 1.94384)
                        u.operation('*', 3.6)         # m/s => km/h
                        v.operation('*', 3.6)

                        uv = epygram.fields.make_vector_field(u, v)
                        ff = uv.to_module()
                        # plot du module seul
                        # fig, ax = ff.cartoplot(minmax=[90, 300],
                        #                        colormap='nipy_spectral',
                        #                        plot_method='contourf',
                        #                        epygram_departments=True,
                        #                        title=f'AROME {exp} Wind Gust (km/h) {date_courante}')

                        titre = (f'AROME-200m-{exp} Refl & Wind '
                                 f'(sampling={SUBSAMPLING}) {date_courante}')
                        fig, ax = uv.cartoplot(fig=fig, ax=ax,
                                               subsampling=SUBSAMPLING,
                                               vector_plot_method='quiver',
                                               subzone='C',
                                               vector_plot_kwargs=QUIVER_KW,
                                               plot_method=None,
                                               title=titre)

                        ax.set_extent(extent_tot, ccrs.PlateCarree())
                        ax.gridlines()

                        # point rouge
                        ax.scatter(lon_point, lat_point, color='white', s=100,
                                   edgecolors='black', marker='o',
                                   transform=ccrs.PlateCarree(),
                                   label="Point d'interet")

                        fic = os.path.join(
                            workdir,
                            f'AROME-200m_{exp}_Wind_Refl_{date_courante}.{FMT}')
                        fig.savefig(fic, dpi=DPI, bbox_inches='tight')
                        plt.close(fig)
                        print(f'  -> {fic}')
                    finally:
                        fcst.close()
