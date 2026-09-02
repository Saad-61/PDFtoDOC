import React from "react";
import { AlertOctagon, RotateCcw, Lock } from "lucide-react";
import { Button } from "../ui/button";

export function ErrorBanner({ error, onReset, onPasswordRequired }) {
  if (!error) return null;

  const isPasswordError =
    error.includes("password") || error.includes("PASSWORD_REQUIRED");

  return (
    <div className="w-full max-w-2xl mx-auto p-5 rounded-md bg-oxblood-surface border border-oxblood-light/40 shadow-xl space-y-3">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-full bg-oxblood/40 border border-oxblood-light/50 flex items-center justify-center flex-shrink-0 text-oxblood-light">
          <AlertOctagon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-ivory">
            Conversion Interrupted
          </h4>
          <p className="text-xs text-taupe mt-1 leading-relaxed">{error}</p>
        </div>
      </div>

      <div className="pt-2 border-t border-oxblood-light/20 flex items-center justify-end gap-2.5">
        {isPasswordError && onPasswordRequired && (
          <Button
            variant="outline"
            size="sm"
            onClick={onPasswordRequired}
            className="border-gold-500/50 text-gold-400 hover:bg-gold-500/10 text-xs"
          >
            <Lock className="w-3 h-3 mr-1.5" />
            Enter Decryption Password
          </Button>
        )}
        <Button
          variant="secondary"
          size="sm"
          onClick={onReset}
          className="text-xs border-slate-border hover:bg-carbon-700"
        >
          <RotateCcw className="w-3 h-3 mr-1.5" />
          Reset Workspace
        </Button>
      </div>
    </div>
  );
}
