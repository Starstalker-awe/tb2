/// <reference lib="dom" />
/// <reference lib="dom.iterable" />

import 'react';
import {createRoot} from 'react-dom/client';

function Component(props: {message: string}) {
    return (
        <h1 className="red">{props.message}</h1>
    )
};

const root = createRoot(document.querySelector("#app")!);
root.render(<Component message="Hello world" />);

// Top references allow document/window to be used; Bun overrides types
// createRoot is React 18