import type { ChangeWebsite } from "../../../activity/activityRequests.ts";
import { useCallback, useEffect, useRef, useState } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { vscodeDark } from "@uiw/codemirror-theme-vscode";
import FormGrouping from "../../FormGrouping.tsx";
import "./CustomLoginScriptForm.scss";
import { Button, FormHelperText } from "@mui/material";
import { checkCustomLoginScript } from "../../../../api/apiRequests.ts";
import {
  CheckIcon,
} from "@heroicons/react/24/outline";

import { useForm } from "../../../form/FormProvider.tsx";
import {completions} from "./codeMirrorLoginScriptLanguage.ts";
import { autocompletion } from "@codemirror/autocomplete";
import { Diagnostic, linter } from "@codemirror/lint";

interface CustomLoginScriptFormProps {
  value: ChangeWebsite;
  onChange?: (value: ChangeWebsite) => void;
  loading?: boolean;
}

export default function CustomLoginScriptForm(
  props: CustomLoginScriptFormProps,
) {
  const { value, onChange, loading } = props;
  const [customAccessEnabled, setCustomAccessEnabled] = useState<boolean>(
    value.custom_login_script !== null,
  );
  const [ error, setError ] = useState<string>("");
  const codeEditorLintingErrors = useRef<Diagnostic[]>([]);
  const [ scriptCorrect, setScriptCorrect ] = useState<boolean>(false);
  const { subscribe, unsubscribe } = useForm();


  function handleEnabledChange(enabled: boolean) {
    setCustomAccessEnabled(enabled);
    setScriptCorrect(false);
    if (!enabled) {
      onChange?.({
        ...value,
        custom_login_script: null,
      });
      setError("");
    }
  }

  function handleCustomLoginScriptChange(val: string) {
    setScriptCorrect(false);
    setError("");
    codeEditorLintingErrors.current = [];
    onChange?.({
      ...value,
      custom_login_script: val,
    });
  }

  const setEditorError = useCallback(
    (errorMessage: string) => {
      if (errorMessage === "") {
        codeEditorLintingErrors.current = [];
        return;
      }

      const match = errorMessage.match(/.*line ([0-9]+) col ([0-9]+).*/);
      if (match) {
        const line = parseInt(match[1]);
        const col = parseInt(match[2]);

        const codeEditorRows = value.custom_login_script?.split("\n") ?? [];
        if(line > codeEditorRows.length) {
          return;
        }

        const from = codeEditorRows.slice(0, line - 1).join("\n").length + col;
        const to = from + codeEditorRows[line - 1].length - col + 1;

        codeEditorLintingErrors.current = [
          {
            from: from,
            to: to,
            severity: "error",
            message: errorMessage,
          },
        ];
      }
    },
    [value.custom_login_script],
  );

  const validate = useCallback(async (): Promise<boolean> => {
    if (!customAccessEnabled) {
      return true;
    }
    const script = value.custom_login_script;
    if(script === "" || script === null) {
      setError("Custom login script can't be empty.");
      return false;
    }
    try {
      const error = await checkCustomLoginScript(script ?? "") ?? "";
      setError(error);
      const valid = error === "";
      setScriptCorrect(valid);
      setEditorError(error);
      return valid;
    } catch {
      setError("Couldn't check syntax. Request failed.");
      setScriptCorrect(false);
      return false;
    }
  }, [value, customAccessEnabled]);

  useEffect(() => {
    const identifier = "custom-login-script";

    subscribe({ identifier: identifier, callback: validate});
    return () => {
      unsubscribe(identifier);
    };
  }, [subscribe, unsubscribe, validate]);


  const lintError = linter(() => {
    return codeEditorLintingErrors.current;
  });

  return (
    <FormGrouping
      className="custom-login-script-form"
      disabled={loading}
      checked={customAccessEnabled}
      onChange={handleEnabledChange}
      elevation={16}
      backgroundElevation={8}
      title="Custom login script (Optional)"
      subtitle="Allows to define a custom login script."
    >
      <div className="custom-login-script-form-container">
        <CodeMirror
          className={`code-editor ${error ? "error" : ""}`}
          value={value.custom_login_script ?? ""}
          onChange={handleCustomLoginScriptChange}
          theme={vscodeDark}
          extensions={[
            autocompletion({
              override: [completions],
              activateOnTyping: true,
            }),
            lintError,
          ]}
        />

        <div className="code-editor-helper-row">
          <FormHelperText
            className="code-editor-error-text"
            error={error !== ""}
          >
            {error.split("\n")[0]}
          </FormHelperText>

          <Button
            variant="outlined"
            size="small"
            onClick={validate}
            startIcon={
              scriptCorrect ? <CheckIcon className="icon" /> : undefined
            }
          >
            Check Syntax
          </Button>
        </div>
      </div>
    </FormGrouping>
  );
}
