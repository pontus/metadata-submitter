import React from "react"

import "@testing-library/jest-dom/extend-expect"
import { render, screen, fireEvent } from "@testing-library/react"
import { Provider } from "react-redux"
import configureStore from "redux-mock-store"
import { toMatchDiffSnapshot } from "snapshot-diff"

import WizardStepper from "../components/NewDraftWizard/WizardComponents/WizardStepper"

const mockStore = configureStore([])

expect.extend({ toMatchDiffSnapshot })

describe("WizardStepper", () => {
  let store
  let wrapper

  beforeEach(() => {
    store = mockStore({
      submissionType: "form",
      wizardStep: 1,
    })
    wrapper = (
      <Provider store={store}>
        <WizardStepper />
      </Provider>
    )
  })

  it("should take a snapshot", () => {
    const { asFragment } = render(wrapper)
    expect(asFragment(wrapper)).toMatchSnapshot()
  })

  it("should have back-step button disabled when navigated to first step", () => {
    const { asFragment } = render(wrapper)
    const firstRender = asFragment()
    const button = screen.getByRole("button", { name: /Back/i })
    fireEvent.click(button)
    expect(firstRender).toMatchDiffSnapshot(asFragment())
  })
})
