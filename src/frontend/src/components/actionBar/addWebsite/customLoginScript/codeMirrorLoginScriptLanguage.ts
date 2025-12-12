import { CompletionContext } from "@codemirror/autocomplete";


export function completions(context: CompletionContext) {
  let word = context.matchBefore(/\w*/);
  if (!word) return null;
  if (word.from == word.to && !context.explicit) return null;
  return {
    from: word.from,
    options: [
      {
        label: "fillUsername()",
        type: "function",
        info: "fillUsername(): Tries to automatically find username text field and fills value.",
      },
      {
        label: 'fillUsername("")',
        type: "function",
        info: "fillUsername(xpath): Fills username in text field found by xpath.",
      },
      {
        label: "fillPassword()",
        type: "function",
        info: "fillPassword(): Tries to automatically find password text field and fills value.",
      },
      {
        label: 'fillPassword("")',
        type: "function",
        info: "fillPassword(xpath): Fills password in text field found by xpath.",
      },
      {
        label: "clickSubmitButton()",
        type: "function",
        info: "clickSubmitButton(): Tries to automatically find submit button and clicks it.",
      },
      {
        label: 'clickSubmitButton("")',
        type: "function",
        info: "clickSubmitButton(xpath): Clicks the submit button found by xpath.",
      },
      {
        label: 'fillText("", "")',
        type: "function",
        info: "fillText(xpath, value): Fills value in text field found by xpath.",
      },
      {
        label: 'clickButton("")',
        type: "function",
        info: "clickButton(xpath): Clicks button found by xpath.",
      },
      {
        label: 'openUrl("")',
        type: "function",
        info: "openUrl(url): Navigates to specified URL.",
      },

      {
        label: "wait(500)",
        type: "function",
        info: "wait(ms): Pauses execution for the specified number of milliseconds.",
      },
    ],
  };
}
