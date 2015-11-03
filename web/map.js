      var zoomOut = 4;
      var zoomIn = 1;
      var tilePath = 'surface/';

      function CustomMapType() {
      }

      mcMapType = new google.maps.ImageMapType({
        getTileUrl: function (coord, zoom) {
          // Our scale starts at 2x2, because centering on 0,0 means we always get four tiles.
          var scale = 1 << zoom;
          // Always stay inside the bounding box.
          if (coord.x < -scale || coord.y < -scale || coord.x >= scale || coord.y >= scale) return null;
          console.log(tilePath + '/z' + (zoomOut-zoom) + '/' + (coord.x) + ',' + (coord.y) + '.png');
          return tilePath + '/z' + (zoomOut-zoom) + '/' + (coord.x) + ',' + (coord.y) + '.png';
        },
        tileSize: new google.maps.Size(512,512),
        isPng: true,
        minZoom: 0,
        maxZoom: zoomIn+zoomOut,
        name: 'Minecraft',
        getTile: function (coord, zoom) {
          var div = ownerDocument.createElement('DIV');
          var url = this.getTileUrl(coord, zoom);
          div.style.width = this.tileSize.width + 'px';
          div.style.height = this.tileSize.height + 'px';
          div.style.backgroundColor = '#1B2D33';
          div.style.backgroundImage = 'url(' + url + ')';
          return div;
        }
      });
      mcMapType.projection = {
        scale: 4096,
        fromLatLngToPoint: function(ll) {
          return new google.maps.Point(ll.lng()*this.scale,ll.lat()*this.scale);
        },
        fromPointToLatLng: function(p) {
          return new google.maps.LatLng(p.y/this.scale, p.x/this.scale);
        }
      };

      util = {
        scale: 4096*(1<<zoomOut),
        fromLatLngToPoint: function(ll) {
          return new google.maps.Point(ll.lng()*this.scale,ll.lat()*this.scale);
        },
        fromPointToLatLng: function(p) {
          return new google.maps.LatLng(p.y/this.scale, p.x/this.scale);
        },
        distance: function(px) {
          return google.maps.geometry.spherical.computeDistanceBetween(
            this.fromPointToLatLng({x:0,y:0}), this.fromPointToLatLng({x:px,y:0})
          );
        }
      };

      console.log(mcMapType.projection.scale);
      CustomMapType.prototype.maxZoom = zoomOut+zoomIn;

      CustomMapType.prototype.getTile = function(coord, zoom, ownerDocument) {
        var div = ownerDocument.createElement('DIV');
        var baseURL = tilePath + 'z' + (zoomOut-zoom) + '/';
        baseURL += coord.x + ',' + coord.y + '.png';
        div.style.width = this.tileSize.width + 'px';
        div.style.height = this.tileSize.height + 'px';
        div.style.backgroundColor = '#1B2D33';
        div.style.backgroundImage = 'url(' + baseURL + ')';
        return div;
      };
      CustomMapType.prototype.name = "Custom";
      CustomMapType.prototype.alt = "Tile Coordinate Map Type";
      var map;
      var CustomMapType = new CustomMapType();

      function initialize() {
        var mapOptions = {

          isPng: true,
          mapTypeControl: false,
          streetViewControl: false,      /* stupid Google thinks the world is a sphere. */
          center: new google.maps.LatLng(0,0),
          zoom: zoomOut,
          mapTypeControlOptions: {
            mapTypeIds: ['custom', google.maps.MapTypeId.ROADMAP],
            style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
          }
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
        map.mapTypes.set('minecraft',mcMapType);
        map.setMapTypeId('minecraft');
new google.maps.Circle({
      center: util.fromPointToLatLng({y:256, x:0}),
      radius: util.distance(1000),
      strokeColor: '#FF0000',
      strokeWeight: 5,
      strokeOpacity: 0.35
    }).setMap(map);
      }


