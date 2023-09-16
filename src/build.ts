import scssLoader from './plugins/scss';
import * as fs from 'fs';

const dirs = ["js", "css"];
for (const dir of dirs) {
	let tmpdir;
	if (!fs.existsSync(tmpdir = `./build/${dir}`)) {
		fs.mkdirSync(tmpdir)
	} else {
		for (const file in fs.readdirSync(tmpdir)) {
			fs.unlinkSync(`${tmpdir}/${file}`)
		}
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
