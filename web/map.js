      var zoomOut = 4;
      var zoomIn = 1;
      var tilePath = 'tiles/';

      function CustomMapType() {
      }

      CustomMapType.prototype.tileSize = new google.maps.Size(512,512);
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
          minZoom: 0,
          maxZoom: zoomIn+zoomOut,
          isPng: true,
          mapTypeControl: false,
          streetViewControl: false,      /* stupid Google thinks the world is a sphere. */
          center: new google.maps.LatLng(85,-180),
          zoom: zoomOut,
          mapTypeControlOptions: {
            mapTypeIds: ['custom', google.maps.MapTypeId.ROADMAP],
            style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
          }
        };
        map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
        map.mapTypes.set('custom',CustomMapType);
        map.setMapTypeId('custom');
      }
