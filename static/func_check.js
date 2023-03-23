// function readURL(input) {
//             if (input.files && input.files[0]) {
//                 var reader = new FileReader();
//
//                 reader.onload = function (e) {
//                     $('#blah')
//                         .attr('src', e.target.result)
//                         .width(150)
//                         .height(200);
//                 };
//
//                 reader.readAsDataURL(input.files[0]);
//             }
//         }

// function image(a,b,c)
// {
//   this.link=a;
//   this.alt=b;
//   this.thumb=c;
// }
//
// function show_image()
// {
//   document.write("img src="+this.link+">");
// }
//
// image1=new image("img/img1.jpg","dsfdsfdsfds","thumb/img3");

// function readURL(input) {
//         if (input.files && input.files[0]) {
//             var reader = new FileReader();
//
//             reader.onload = function (e) {
//                 $('#blah').attr('src', e.target.result);
//             }
//
//             reader.readAsDataURL(input.files[0]);
//         }
//     }
//
//     $("#imgInp").change(function(){
//         readURL(this);
//     });


const image_input = document.querySelector("#firstname");
var uploaded_image = "";
image_input.addEventListener("change",function (){
    console.log(image_input.value);
    const reader = new FileReader();
    reader.addEventListener("load",()=>{
        uploaded_image=reader.result;
        document.querySelector("#firstname")
    });
    reader.readAsDataURL(this.files[0]);
})