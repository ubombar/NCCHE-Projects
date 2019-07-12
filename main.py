import ogr

def ogrinfo_print_layers(filename):
    ds = ogr.Open(filename, 0)

    if ds is None:
        raise OSError('Failed to open {}'.format(filename))
    
    for lys in ds:
        print('{} {}'.format('layer name: ', lys.GetName()))

# ogrinfo_print_layers('data/areas.geojson')

ds = ogr.Open('data/ports.geojson', 0)

print(ds.GetLayer().GetName())

flyr = ds.ExecuteSQL("SELECT fid, name FROM ports WHERE fid=3")

for col in flyr:
    print(col.GetField('fid'), col.GetField('name'))