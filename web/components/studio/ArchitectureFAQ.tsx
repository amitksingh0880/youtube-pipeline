"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { ARCHITECTURE_FAQS } from "@/config/studio-config";

export function ArchitectureFAQ() {
  return (
    <Card className="shadow-sm border-border/60">
      <CardHeader className="py-3 px-4">
        <CardTitle className="text-sm font-semibold">Technical Reference & FAQ</CardTitle>
        <CardDescription className="text-xs">
          Learn more about pipeline options, memory limits, and automated cloud fallback configurations.
        </CardDescription>
      </CardHeader>
      <CardContent className="px-4 pb-4 pt-0">
        <Accordion className="w-full">
          {ARCHITECTURE_FAQS.map((faq) => (
            <AccordionItem key={faq.id} value={faq.id}>
              <AccordionTrigger className="text-xs font-semibold py-2.5">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-xs text-muted-foreground leading-relaxed">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </CardContent>
    </Card>
  );
}
