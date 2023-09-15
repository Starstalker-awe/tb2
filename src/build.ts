import scssLoader from './plugins/scss';
import * as fs from 'fs';

for (const folder in ["js", "css"]) {
    for (const file in fs.readdirSync(`./build/${folder}`)) {
        fs.unlinkSync(`./build/${folder}/${file}`)
    }
}

const entrypoints = [
    ...fs.readdirSync("./js").map((n: string) => `./js/${n}`),
    ...fs.readdirSync("./scss").map((n: string) => `./scss/${n}`)
];

await Bun.build({
    entrypoints: entrypoints,
    outdir: "./build/js/",
    splitting: true,
    minify: true,
    plugins: [
        scssLoader
    ]
});