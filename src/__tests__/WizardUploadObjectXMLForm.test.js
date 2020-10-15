import React from "react"

import "@testing-library/jest-dom/extend-expect"
import { render, screen } from "@testing-library/react"
// import userEvent from "@testing-library/user-event"
import { Provider } from "react-redux"
import configureStore from "redux-mock-store"
import { toMatchDiffSnapshot } from "snapshot-diff"

import WizardUploadObjectXMLForm from "../components/NewDraftWizard/WizardForms/WizardUploadObjectXMLForm"

const mockStore = configureStore([])

expect.extend({ toMatchDiffSnapshot })

describe("WizardStepper", () => {
  const store = mockStore({
    submissionType: "form",
    submissionFolder: {
      description: "AWD",
      id: "FOL90524783",
      name: "Testname",
      published: false,
    },
  })

  it("should have send button disabled when there's no validated xml file", () => {
    render(
      <Provider store={store}>
        <WizardUploadObjectXMLForm />
      </Provider>
    )
    expect(screen.getByRole("button", { name: /save/i })).toHaveAttribute("disabled")
  })

  // it("should enable save button when there's validated xml file", async () => {
  //   // const file = new File(["test"], "test.xml", { type: "xml" })
  //   render(
  //     <Provider store={store}>
  //       <WizardUploadObjectXMLForm />
  //     </Provider>
  //   )
  //   // const input = screen.getByRole("textbox")
  //   // userEvent.upload(input, file)
  //   // fireEvent.change(input, {
  //   //   target: {
  //   //     value: [file],
  //   //   },
  //   // })
  //   // expect(screen.getByRole("button", { name: /save/i })).toHaveAttribute("disabled")
  //   expect(screen.getByText(/Please attach an XML file./i)).toBeDefined()
  //   screen.debug()
  // })
})
