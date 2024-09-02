let status = "emp1"

document.getElementById("empresa").onchange = function(){
    let value = this.value

    let images = document.querySelectorAll("img") 
    images.forEach( (image) => image.src = image.src.replace(status, value) )

    let iframe = document.querySelector("iframe")
    iframe.src = iframe.src.replace(status,value)

    status = value
}