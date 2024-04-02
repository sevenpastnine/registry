import { printf, toConsole } from "./fable_modules/fable-library.4.5.0/String.js";
import { some } from "./fable_modules/fable-library.4.5.0/Option.js";

toConsole(printf("Hello World from F#"));

export const a = 4;

console.log(some(a));

