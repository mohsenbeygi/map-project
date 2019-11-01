var osmread = require('osm-read');
osmread.pbfParser.parse({
    filePath: 'highways.osm',
    endDocument: function(){
        console.log('document end');
    },
    node: function(node){
        console.log('node: ' + JSON.stringify(node));
    },
    way: function(way){
        console.log('way: ' + JSON.stringify(way));
    },
    relation: function(relation){
        console.log('relation: ' + JSON.stringify(relation));
    },
    error: function(msg){
        console.error('error: ' + msg);
        throw msg;
    }
});
