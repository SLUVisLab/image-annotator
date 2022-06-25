// Responible for loading in image on canvas, drawing rectangle on image, and sending resulting coordinates back to index.html

// Canvas
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// Image
var img = new Image();
img.src = document.getElementById("canvas_script").getAttribute("data-url");
var img_scale_ratio = .15;

// Keeping track of dynamic coordinates
var last_mousex = last_mousey = 0;
var mousex = mousey = 0;
var canvasx, canvasy;
var mousedown = false;

// Storing rectangle corner coordinates
var xmin, xmax, ymin, ymax;


// Loading in the image
img.onload = () => {

    // resizing the canvas to fit a scaled image
    canvas.width = img.width * img_scale_ratio;
    canvas.height = img.height * img_scale_ratio;
    // store coordinates of top left corner of canvas
    canvasx = canvas.getBoundingClientRect().left;
    canvasy = canvas.getBoundingClientRect().top;
    // draw image on canvas, send image size to index.html
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    document.getElementById("img_size").innerHTML = "Image Size = [" + img.width + ", " + img.height + "]";

    // check if there is existing bbox information stored for the image
    var existing_bbox = document.getElementById("bbox_scaled").innerHTML;
    try {
        // works if bbox is in format [xmin, xmax, ymin, ymax]
        // extract information into array of ints and scale coordinates to fit canvas
        var existing_bbox_parsed = existing_bbox.replace("Bounding Box = ", "").replace("[", "").replace("]", "").split(",");
        console.log(existing_bbox_parsed);
        var existing_bbox_parsed = existing_bbox_parsed.map(function (x) { 
            return Math.round(parseInt(x) * img_scale_ratio); 
        });

        // draw rectangle with coordinates
        ctx.rect(existing_bbox_parsed[0], existing_bbox_parsed[2], existing_bbox_parsed[1] - existing_bbox_parsed[0], existing_bbox_parsed[3] - existing_bbox_parsed[2]);
        ctx.strokeStyle = '#1B9AFF';
        ctx.lineWidth = 2;
        ctx.stroke();
    } catch {
        // ignore
    }
};

// Mousedown
$(canvas).on('mousedown', function(e) {
    // store coordinates
    last_mousex = (e.clientX - canvasx);
    last_mousey = (e.clientY - canvasy);
    mousedown = true;
});

// Mouseup
$(canvas).on('mouseup', function(e) {
    // store coordinates
    last_mousex = (e.clientX - canvasx);
    last_mousey = (e.clientY - canvasy);
    mousedown = false;
    // send unscaled bbox coordinates to index.html
    var bbox = "[" + Math.round(xmin / img_scale_ratio) + ", " + Math.round(xmax / img_scale_ratio) + ", " + 
                     Math.round(ymin / img_scale_ratio) + ", " + Math.round(ymax / img_scale_ratio) + "]";
    document.getElementById("bbox_scaled").innerHTML = "Bounding Box = " + bbox;
    document.getElementById("bbox_value").value = bbox;
});

// Mousemove
$(canvas).on('mousemove', function(e) {
    // store coordinates
    mousex = (e.clientX - canvasx);
    mousey = (e.clientY - canvasy);
    if(mousedown) {
        // clear canvas and redraw image
        ctx.clearRect(0, 0, canvas.width, canvas.height); 
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        // draw rectangle
        ctx.beginPath();
        var width = mousex - last_mousex;
        var height = mousey - last_mousey;
        ctx.rect(last_mousex, last_mousey, width, height);
        ctx.strokeStyle = '#1B9AFF';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.closePath();
        // store rectangle corner coordinates
        xmin = Math.min(last_mousex, mousex);
        xmax = Math.max(last_mousex, mousex);
        ymin = Math.min(last_mousey, mousey);
        ymax = Math.max(last_mousey, mousey);
    }
});
