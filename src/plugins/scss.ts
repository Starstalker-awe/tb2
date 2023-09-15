import {type BunPlugin} from 'bun';
import {compile} from 'sass';
import * as fs from 'fs';

const scssLoader: BunPlugin = {
    name: "SCSS Compiler",
    setup(build) {
        for (const file of build.config.entrypoints.filter(n => n.endsWith(".scss"))) {
            fs.writeFileSync(`./build/css/${file.split('/').at(-1)?.split('.')[0]}.css`, compile(file, {style: "compressed"}).css);
            build.config.entrypoints = build.config.entrypoints.filter(n => n != file);
        }
    }
};

export default scssLoader;