
$(document).ready(function() {

  // create canvas
  const frame = document.getElementById('canvasFrame');
  const canvas = document.createElement('canvas');
  const width = frame.offsetWidth;
  const height = 300;
  canvas.height = height;
  canvas.width = width;
  canvas.id = "plaidCanvas";
  canvas.classList.add("center")
  frame.appendChild(canvas);

  // canvas constants
  const ctx = canvas.getContext("2d");

  // program constants
  const background = new Base(parseColor($("#base").val()));
  const lineArray = [];

  // Object constructors
  function Base(color) {
    this.color = color; // return value of parseColor() call
    this.draw = function(ctx, width, height) {
      if (this.color !== undefined) {
        ctx.fillStyle = this.color;
        var background = new Path2D();
        background.rect(0, 0, width, height);
        ctx.fill(background);
      }
    };
  };

  function Line() {

    // attributes
    this.color = parseColor("#000000", true); // return value of parseColor() call
    this.thickness = 1;
    this.regularity = 1;
    this.orientation = "h"; // can be h for horizontal, v for vertical or b for both

    // methods
    this.draw = function() {
      console.log("line draw initiated");

      ctx.save();
      console.log(this.color);
      ctx.fillStyle = this.color;


      // each orientation has an offset, making offset an array of len of
      // space between lines

      let offset;
      let div = parseInt(this.regularity) + 1;
      console.log('div: ' + div);
      if (this.orientation === 'h') {
        offset = [[height / div, 'h']];
      } else if (this.orientation === 'v') {
        offset = [[width / div, 'v']];
      } else if (this.orientation === 'b') {
        offset = [[height / div, 'h'], [width / div, 'v']];
      }

      console.log('offset length: ' + offset.length);

      // one for each orientation
      for (let i = 0; i < offset.length; i++) {
        console.log('i = ' + i);
        console.log('offset: ' + offset[i])

        for (let j = 0; j < this.regularity; j++) {
          console.log('j = ' + j);
          // possibly clean this up by variable swapping???
          let a = (offset[i][0] * (j + 1)) - (this.thickness / 2);

          console.log('a = ' + a)


          if (offset[i][1] === 'h') {
            ctx.fillRect(0, a, width, this.thickness);
            console.log('rectangle draw command: h');
          } else if (offset[i][1] === 'v') {
            console.log('rectangle draw command: v')
            ctx.fillRect(a, 0, this.thickness, height);
          };
        };
      };

      ctx.restore();
      console.log('line drawing concluded');
    };
  };




  // convert value from color element into string readable by fillStyle
  function parseColor(colorString, isLine) {
    var red = parseInt("0x" + colorString.slice(1,3));
    var green = parseInt("0x" + colorString.slice(3,5));
    var blue = parseInt("0x" + colorString.slice(5,7));
    var a;
    if (isLine) {
      a = .5;
    }
    else {
      a = 1;
    }
    var output = 'rgba(' + red.toString() + ',' + green.toString() + ',' +
    blue.toString() + ',' + a.toString() + ')';
    return output;
  }

  // add lines to pattern
  function addLine() {
    console.log('addLine begin')

    var sliderWidth = '7px'

    var panel = document.getElementById('controlPanel');
    var index = lineArray.length;

    // create element and add it to panel
    var newLine = document.createElement('div');
    newLine.classList.add('line-frame');
    panel.appendChild(newLine);

    // define name new line attributes
    newLine.id = 'line' + index.toString();

    // add headerd
    var header = document.createElement('h3');
    var content = document.createTextNode('Line ' + (index + 1).toString());
    header.appendChild(content);
    newLine.appendChild(header);

    // add inputs box
    var inputBox = document.createElement('div');
    inputBox.classList.add('innerInputContainer');
    newLine.appendChild(inputBox);

    // create flexboxes and add to div;
    var colorBox = document.createElement('div');
    inputBox.appendChild(colorBox);
    colorBox.classList.add('lineAttrContainer');
    var thiccBox = document.createElement('div');
    inputBox.appendChild(thiccBox);
    thiccBox.classList.add('lineAttrContainer');
    var regBox = document.createElement('div');
    inputBox.appendChild(regBox);
    regBox.classList.add('lineAttrContainer');
    var orientBox = document.createElement('div');
    inputBox.appendChild(orientBox);
    orientBox.classList.add('lineAttrContainer');

    // add descriptors to the flexboxes
    var colorHeader = document.createElement('h4');
    colorHeader.appendChild(document.createTextNode('Color'))
    colorBox.appendChild(colorHeader);

    var thiccHeader = document.createElement('h4');
    thiccHeader.appendChild(document.createTextNode('Size'))
    thiccBox.appendChild(thiccHeader);

    var regHeader = document.createElement('h4');
    regHeader.appendChild(document.createTextNode('Quantity'))
    regBox.appendChild(regHeader);

    var orientHeader = document.createElement('h4');
    orientHeader.appendChild(document.createTextNode('Orient'))
    orientBox.appendChild(orientHeader);


    // create line

    var newLineObject = new Line()
    newLineObject.color = parseColor('#ff0000', true);
    lineArray.push(newLineObject);

    // add color input
    var lineColor = document.createElement('input');
    lineColor.type = 'color';
    lineColor.value = '#ff0000';
    lineColor.classNameName = 'line';
    lineColor.id = 'C' + index;
    colorBox.appendChild(lineColor);
    $('#C' + index).change(function () {
      console.log('line color change registered');
      let lineObject = lineArray[event.target.id[1]];
      lineObject.color = parseColor(event.target.value, true);

      draw();
    });

    // add thickness input
    var lineThickness = document.createElement('input');
    lineThickness.type = 'range';
    lineThickness.value = 1;
    lineThickness.className = 'line';
    lineThickness.id = 'T' + index.toString();
    lineThickness.min = 1;
    lineThickness.max= 50;
    lineThickness.width = sliderWidth;
    thiccBox.appendChild(lineThickness);
    $('#T' + index).change(function () {
      console.log('line thickness change registered');
      let lineObject = lineArray[event.target.id[1]];
      lineObject.thickness = event.target.value;

      draw();
    });

    // add regularity input
    var lineRegularity = document.createElement("input");
    lineRegularity.type = 'range';
    lineRegularity.value = 1;
    lineRegularity.className = 'line';
    lineRegularity.id = 'R' + index.toString();
    lineRegularity.min = 1;
    lineRegularity.max = 20;
    lineRegularity.width = sliderWidth;
    regBox.appendChild(lineRegularity);
    $('#R' + index).change(function () {
      console.log('line regularity change registered');
      let lineObject = lineArray[event.target.id[1]];
      lineObject.regularity = event.target.value;

      draw();
    });

    // add orientation seletor
    var lineReorient = document.createElement('select');

    lineReorient.id = 'O' + index.toString();

    lineReorient.addEventListener('change', function(e) {

      console.log(e)
      let sel = e.target;
      let id = sel.id;
      console.log(id);
      let value = sel.value;
      let lineObject = lineArray[id[1]];

      lineObject.orientation = value[0];

      draw();
    });

    //lineReorient.setAttribute('onchange', 'changeOrientation(this)');

    var orients = ['horizontal', 'vertical', 'both'];

    for (let i = 0; i < orients.length; i++) {
      orient = orients[i];
      var option = document.createElement("option");
      option.value = orient.slice(0,2);
      option.appendChild(document.createTextNode(orient));
      lineReorient.appendChild(option);
    }

    orientBox.appendChild(lineReorient);

    draw();
  }




  function draw() {

    // initialize background
    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.fillStyle = background.color;
    ctx.fillRect(0,0, width, height);
    ctx.restore();

    for (let i = 0; i < lineArray.length; i++) {
      lineArray[i].draw();
    }

  }



  var lineButton = document.getElementById("addLine");
  lineButton.addEventListener('click', addLine);


  // initialize background
  draw()

  $("#base").change(function () {
    background.color = parseColor($("#base").val(), false);
    console.log("change registered");
    console.log(background.color);
    ctx.clearRect(0, 0, width, height);

    draw();
  });
});
