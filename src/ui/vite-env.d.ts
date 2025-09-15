/// <reference types="vite/client" />
declare module "*.png";
declare module "*.svg";
declare module "*.jpeg";
declare module "*.jpg";
 
declare module "*.jpg" {
    export default "" as string;
}
declare module "*.png" {
    export default "" as string;
}