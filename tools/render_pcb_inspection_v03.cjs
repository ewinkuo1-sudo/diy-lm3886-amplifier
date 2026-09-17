// SVG->PNG without modifying the vector source. Requires sharp in NODE_PATH.
const fs=require('fs'),path=require('path'),sharp=require('sharp');
const dir=path.resolve(__dirname,'../pcb/inspection-v03/drawings');
(async()=>{for(const f of fs.readdirSync(dir).filter(f=>f.endsWith('.svg')))await sharp(path.join(dir,f)).png().toFile(path.join(dir,f.replace('.svg','.png')));})();
