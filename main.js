osmread.createPbfParser({
    filePath: 'path/to/osm.pbf',
    callback: function(err, parser){
        var headers;

        if(err){
            // TODO handle error
        }

        headers = parser.findFileBlocksByBlobType('OSMHeader');

        parser.readBlock(headers[0], function(err, block){
            console.log('header block');
            console.log(block);

            parser.close(function(err){
                if(err){
                    // TODO handle error
                }
            });
        });
    }
});
