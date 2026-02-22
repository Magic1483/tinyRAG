"use client"

import Image from "next/image";
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
  FieldLegend,
  FieldSeparator,
  FieldSet,
  FieldTitle,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import React from "react";
import { API_BASE } from "../api";


type Config = {
  embedded_model: string;
  model: string;
  model_url: string;
}

export default function Settings() {

  const [embedModel, setEmbedModel] = React.useState("")
  const [model, setModel] = React.useState("")
  const [modelUrl, setModelUrl] = React.useState("")
  const [config, setConfig] = React.useState<Config | null>(null)

  React.useEffect(() => {
    async function getConfig() {
      const res = await fetch(`${API_BASE}/config`);
      if (!res.ok) return
      const config: Config = await res.json()
      setConfig(config)
      setEmbedModel(config.embedded_model)
      setModel(config.model)
      setModelUrl(config.model_url)
    }

    getConfig()
  }, [])


  async function updateConfig() {
    if (!model || !modelUrl || !embedModel) return

    const res = await fetch(`${API_BASE}/config`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: model,
        model_url: modelUrl,
        embedded_model: embedModel,
      }),
    })
  }

  return (
    <div className="">
      <div className="w-[70%] max-w-[800px] m-auto mt-12 border rounded p-4">
        <form>
          <FieldGroup>
            <FieldSet>
              <FieldLegend>Settings</FieldLegend>
            </FieldSet>
            <FieldGroup >
              <Field className="flex flex-row ">
                <FieldLabel htmlFor="embed-label">Embeded model</FieldLabel>
                <Input id="embed-model" required value={embedModel} onChange={(e) => setEmbedModel(e.target.value)} />
              </Field>
              <Field className="flex flex-row">
                <FieldLabel htmlFor="embed-label">LLM Model</FieldLabel>
                <Input id="embed-model" required value={model} onChange={(e) => setModel(e.target.value)} />
              </Field>
              <Field className="flex flex-row">
                <FieldLabel htmlFor="embed-label">Model endpoint</FieldLabel>
                <Input id="embed-model" required value={modelUrl} onChange={(e) => setModelUrl(e.target.value)} />
              </Field>
              <Button variant={"outline"} className="cursor-pointer" disabled >Apply</Button>
            </FieldGroup>
          </FieldGroup>
        </form>
      </div>
    </div>
  );
}
